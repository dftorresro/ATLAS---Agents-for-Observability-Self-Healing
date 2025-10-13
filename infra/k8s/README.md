# Kubernetes / KubeRay / OpenTelemetry / Datadog (guidance)

This first commit keeps everything **local**. In subsequent commits:

1. Install **KubeRay** on your cluster (kind/minikube or managed).
2. Deploy **RayCluster**, **RayService** for model serving, and **RayJob** for training.
3. Run the **OpenTelemetry Collector** with a Datadog exporter or run the Datadog Agent.
4. Instrument your services with OpenTelemetry SDKs and/ or ddtrace.
5. Configure RBAC-scoped action tools for the SRE agent (scale/restart/rollback).

Keep CRDs versioned in this folder.
