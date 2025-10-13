"""Placeholder utilities for real Kubernetes actions (not used in first commit).

In later commits, you can implement guarded kubectl calls or Kubernetes Python API calls.
All functions should:
- Validate inputs
- Respect dry-run
- Emit structured logs/metrics/traces
- Enforce RBAC scope and human approvals where required
"""

def restart_deployment(name: str, namespace: str = "default", dry_run: bool = True) -> None:
    raise NotImplementedError("Add guarded kubectl or Kubernetes API calls here.")

def scale_deployment(name: str, delta: int, namespace: str = "default", dry_run: bool = True) -> None:
    raise NotImplementedError("Add guarded kubectl or Kubernetes API calls here.")

def rollback_deployment(name: str, namespace: str = "default", dry_run: bool = True) -> None:
    raise NotImplementedError("Add guarded kubectl or Kubernetes API calls here.")
