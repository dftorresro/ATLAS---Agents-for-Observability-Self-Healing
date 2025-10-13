from __future__ import annotations
import logging
logger = logging.getLogger("atlas.agent.tools.simulator")

def restart_service(service: str) -> None:
    logger.info(f"[simulator] restart_service: service={service} -> simulated restart OK")

def scale_service(service: str, delta: int) -> None:
    logger.info(f"[simulator] scale_service: service={service} delta={delta} -> simulated scale OK")

def rollback_service(service: str) -> None:
    logger.info(f"[simulator] rollback_service: service={service} -> simulated rollback OK")

def gather_diagnostics(minutes: int) -> None:
    logger.info(f"[simulator] gather_diagnostics: minutes={minutes} -> simulated collection OK")
