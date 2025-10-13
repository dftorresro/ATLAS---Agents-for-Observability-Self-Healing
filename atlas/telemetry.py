from __future__ import annotations
import logging
import os

logger = logging.getLogger("atlas")
_handler = logging.StreamHandler()
_formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel(logging.INFO)

def init_telemetry(service_name: str = "atlas") -> None:
    """Initialize basic logging and (optionally) OpenTelemetry tracing.

    - Uses stdlib logging by default.
    - If ATLAS_ENABLE_OTEL=1 and opentelemetry is installed, configures a basic tracer.
    - If ATLAS_ENABLE_DDTRACE=1 and ddtrace is installed, enables ddtrace autopatching.
    """
    # stdlib logging already configured above.
    if os.getenv("ATLAS_ENABLE_OTEL") == "1":
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

            provider = TracerProvider()
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            logger.info("OpenTelemetry tracer initialized (ConsoleSpanExporter).")
        except Exception as e:  # pragma: no cover - best-effort optional
            logger.warning(f"Could not initialize OpenTelemetry: {e}")

    if os.getenv("ATLAS_ENABLE_DDTRACE") == "1":
        try:
            import ddtrace  # type: ignore
            ddtrace.patch_all()
            logger.info("ddtrace auto-instrumentation enabled.")
        except Exception as e:  # pragma: no cover - best-effort optional
            logger.warning(f"Could not enable ddtrace: {e}")
