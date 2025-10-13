from __future__ import annotations
import os
import typer
from rich.console import Console
from rich.table import Table
import pandas as pd

from atlas.telemetry import init_telemetry, logger
from atlas.data.simulated_metrics import generate_cpu_series, save_csv
from atlas.models.anomaly import rolling_zscore_anomalies
from atlas.agent.sre_agent import SREAgent

app = typer.Typer(add_completion=False, help="""Atlas CLI (first commit)
- simulate: generate synthetic metrics
- detect: run a simple anomaly detector
- agent run: end-to-end dry-run incident flow
""")

console = Console()

@app.callback()
def _root():
    init_telemetry()

@app.command()
def simulate(minutes: int = typer.Option(180), spike_at: int | None = typer.Option(60), drift_at: int | None = typer.Option(120), out: str = typer.Option("data/cpu.csv", help="Output CSV path")):
    """Generate a synthetic CPU time series with optional anomalies."""
    df = generate_cpu_series(minutes=minutes, spike_at=spike_at, drift_at=drift_at)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    save_csv(df, out)
    console.print(f"[bold green]Wrote[/bold green] {out} ({len(df)} rows)")

@app.command()
def detect(file: str = typer.Option("data/cpu.csv"), window: int = 30, threshold: float = 3.0):
    """Run rolling z-score anomaly detection on a CSV file (minute,cpu_util)."""
    df = pd.read_csv(file)
    res = rolling_zscore_anomalies(df["cpu_util"], window=window, threshold=threshold)
    table = Table(title="Anomaly Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Count", str(len(res.indices)))
    table.add_row("Threshold (|z|)", f"{threshold}")
    if res.indices:
        table.add_row("First index", str(res.indices[0]))
        table.add_row("Last index", str(res.indices[-1]))
    console.print(table)

@app.command("agent")
def agent_cmd():
    """Namespace for agent commands."""
    pass

@agent_cmd.command("run")
def agent_run(file: str = typer.Option("data/cpu.csv"), auto_approve: bool = typer.Option(False), dry_run: bool = typer.Option(True)):
    """End-to-end: detect → diagnose → plan → (optionally) act."""
    df = pd.read_csv(file)
    agent = SREAgent(dry_run=dry_run)
    detection = agent.detect(df, metric="cpu_util")
    diag = agent.diagnose(detection)
    console.print(f"[bold]Diagnosis:[/bold] {diag}")
    plan = agent.plan(detection)
    for i, step in enumerate(plan.steps, start=1):
        console.print(f"[cyan]Plan {i}:[/cyan] {step.description} [dim]({step.action} {step.params})[/dim]")
    agent.act(plan, auto_approve=auto_approve)
    console.print("[bold green]Done.[/bold green]")

if __name__ == "__main__":
    app()
