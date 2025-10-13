from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging
import pandas as pd
from atlas.models.anomaly import rolling_zscore_anomalies, AnomalyResult
from atlas.agent.tools import simulator

logger = logging.getLogger("atlas.agent")

@dataclass
class Detection:
    has_anomaly: bool
    indices: list[int]
    kind: Optional[str] = None  # 'spike' or 'drift' (heuristic)

@dataclass
class PlanStep:
    description: str
    action: str
    params: Dict[str, Any]
    requires_approval: bool = True

@dataclass
class Plan:
    steps: List[PlanStep]
    rationale: str

class SREAgent:
    """Minimal SRE agent: detect → diagnose → plan → (optionally) act."""
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def detect(self, df: pd.DataFrame, metric: str = "cpu_util") -> Detection:
        res: AnomalyResult = rolling_zscore_anomalies(df[metric], window=30, threshold=3.0)
        has = len(res.indices) > 0
        kind = self._classify(df[metric], res)
        logger.info(f"Detection: has_anomaly={has}, kind={kind}, count={len(res.indices)}")
        return Detection(has_anomaly=has, indices=res.indices, kind=kind)

    def _classify(self, s: pd.Series, res: AnomalyResult) -> Optional[str]:
        # Heuristic: if many consecutive positives late in the series -> drift; else spike
        if not res.indices:
            return None
        idx = res.indices
        if len(idx) >= 3 and (idx[-1] - idx[-3]) <= 10:
            return "spike"
        # Look at last window trend
        tail = s.iloc[-30:]
        if tail.diff().mean() > 0.15:
            return "drift"
        return "spike"

    def diagnose(self, detection: Detection) -> str:
        if not detection.has_anomaly:
            return "No active anomaly detected."
        if detection.kind == "spike":
            return "Likely bursty load or a stuck worker; restart and scale out temporarily."
        if detection.kind == "drift":
            return "Gradual capacity leak or regression; roll back recent release and scale up."
        return "Unknown anomaly pattern; gather more context."

    def plan(self, detection: Detection) -> Plan:
        steps: List[PlanStep] = []
        if detection.kind == "spike":
            steps = [
                PlanStep("Restart the service to clear stuck workers", "restart", {"service": "checkout"}, True),
                PlanStep("Scale out HPA by +1 replica for 30m", "scale", {"service": "checkout", "delta": +1}, True),
            ]
            rationale = "Short spike; restart + transient scale-out should reduce saturation."
        elif detection.kind == "drift":
            steps = [
                PlanStep("Roll back to previous stable version", "rollback", {"service": "checkout"}, True),
                PlanStep("Scale up HPA permanently by +1", "scale", {"service": "checkout", "delta": +1}, True),
            ]
            rationale = "Sustained drift; rollback potential regression and add capacity."
        else:
            steps = [PlanStep("Gather diagnostics (logs/traces)", "gather", {"minutes": 10}, False)]
            rationale = "No clear classification; collect more context."
        logger.info(f"Plan: {len(steps)} steps, rationale='{rationale}'")
        return Plan(steps=steps, rationale=rationale)

    def act(self, plan: Plan, auto_approve: bool = False) -> None:
        for i, step in enumerate(plan.steps, start=1):
            logger.info(f"[Step {i}] {step.description} -> {step.action} {step.params} (approval={'yes' if step.requires_approval else 'no'})")
            if step.requires_approval and not auto_approve and self.dry_run:
                logger.info("DRY-RUN: approval required; skipping execution.")
                continue
            self._execute(step)

    def _execute(self, step: PlanStep) -> None:
        # In first commit, route to simulator only; real k8s hooks will be added later.
        action = step.action
        params = step.params
        if self.dry_run:
            logger.info(f"DRY-RUN: would execute '{action}' with {params}")
            return
        if action == "restart":
            simulator.restart_service(params.get("service", "app"))
        elif action == "scale":
            simulator.scale_service(params.get("service", "app"), int(params.get("delta", 1)))
        elif action == "rollback":
            simulator.rollback_service(params.get("service", "app"))
        elif action == "gather":
            simulator.gather_diagnostics(int(params.get("minutes", 10)))
        else:
            logger.warning(f"Unknown action '{action}' (no-op)")
