# Atlas — Agents for Observability & Self-Healing

## Quickstart (Python 3.10+)

```bash
git clone <your-repo-url> atlas
cd atlas

python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"     # installs runtime + dev deps

# 1) Generate a synthetic metrics timeseries with injected anomalies
atlas simulate --minutes 180 --spike-at 60 --drift-at 120 --out data/cpu.csv

# 2) Run simple anomaly detection (rolling z-score) and print a summary
atlas detect --file data/cpu.csv

# 3) Run the SRE agent end-to-end in dry-run mode (no real cluster actions)
atlas agent run --file data/cpu.csv --dry-run

# 4) Run tests & lint
pytest -q
ruff check .
```

## Repo layout (first commit)
```
atlas/
  agent/
    __init__.py
    sre_agent.py          # detect→diagnose→plan→act (dry-run by default)
    tools/
      __init__.py
      kubernetes.py       # optional kubectl actions (guarded, dry-run safe)
      simulator.py        # local "actions" for demo (restart/scale, mocked)
  data/
    __init__.py
    simulated_metrics.py  # synthetic CPU series with spike/drift anomalies
  models/
    __init__.py
    anomaly.py            # rolling z-score + naive forecast baseline
  telemetry.py            # logging + optional OpenTelemetry/ddtrace hooks
  cli.py                  # Typer CLI entrypoint: `atlas`

benchmarks/               # placeholders and README
dashboards/               # placeholders and README
infra/
  k8s/README.md           # guidance to add KubeRay, OTel Collector
  local/README.md         # local/dev notes
tests/
  test_anomaly.py

pyproject.toml            # package metadata + dependencies
requirements.txt          # convenience mirror of runtime deps
LICENSE                   # MIT
README.md                 # this file
.gitignore
.env.example              # credentials placeholders for later integrations
.github/workflows/ci.yml  # minimal CI (lint + tests)
```

## What’s included in this commit

- **Synthetic telemetry generator** you can expand or swap with real OTel sources.
- **Baseline anomaly detector** (rolling z-score) as a placeholder for a foundation model (e.g., Toto).
- **SRE agent skeleton** with clear phases and safe action tooling (dry-run + human-in-the-loop flags).
- **Observability hooks** for tracing/metrics via logging (and optional OTel/ddtrace if installed).
- **Tests & CI** to enforce quality from day one.

## Roadmap (how to extend)
- **Replace baseline anomalies** with a foundation model (e.g., Toto) and serve via Ray Serve.
- **Add distributed training** via Ray Train/Tune; add BOOM/NAB benchmarks.
- **Add KubeRay + real actions** (scale/restart/rollback) guarded by RBAC and approvals.
- **Add code repair agent** that proposes patches gated by tests, creating a draft PR.
- **Instrument research stack** with Ray integration, LLM Observability, ddtrace/DogStatsD.

---

**Safety & Cost**: Everything defaults to **dry-run** with explicit prompts before any system‑level action.
Integrations requiring credentials are **off** unless you configure `.env` and the respective toggles.


