# SentinelRAG Troubleshooting Guide

This guide explains how to investigate common API, Kubernetes, and monitoring issues in SentinelRAG.

## 1. Check API Health

Run:

```bash
curl -i http://<API-ENDPOINT>/health
```

Expected result: HTTP 200 with a healthy status.

If the request fails, check the API endpoint, network connectivity, and Kubernetes deployment.

## 2. Check Kubernetes Pods

```bash
kubectl get deployment sentinelrag-api
kubectl get pods -n default -o wide
```

Check application logs:

```bash
kubectl logs deployment/sentinelrag-api --tail=100
```

Common issues:

- `CrashLoopBackOff`: inspect application logs and startup configuration.
- `ImagePullBackOff`: verify the container image, tag, and registry permissions.
- `Pending`: inspect pod events, node capacity, and resource requests.

## 3. Troubleshoot SentinelRAGAPIDown

This alert means Prometheus could not successfully scrape the configured API metrics target for the configured evaluation period. It does not necessarily mean the application has crashed.

Open the Prometheus targets page:

http://localhost:9090/targets

Or run:

```bash
curl -s http://localhost:9090/api/v1/targets
```

Find the `sentinelrag-api` target and inspect:

- `health`: whether the target is `up` or `down`
- `lastError`: the most recent scrape error
- `lastScrape`: when Prometheus last tried to scrape the target

If the target is down, check the API endpoint, `/metrics` path, and network connectivity from Prometheus to the API.

## 4. Check the Metrics Endpoint

```bash
curl -i http://<API-ENDPOINT>/metrics
```

If the endpoint works from your Mac but Prometheus reports it as down, investigate connectivity from the Prometheus container.

## 5. Check Docker and Monitoring

If Docker reports that it cannot connect to the Docker daemon:

1. Open Docker Desktop.
2. Wait until the Docker engine is running.
3. Check containers:

   ```bash
   docker ps
   ```

Start the monitoring stack:

```bash
docker compose -f monitoring/compose.yaml up -d
```

Check service status:

```bash
docker compose -f monitoring/compose.yaml ps
```

The stack contains Prometheus, Grafana, and Alertmanager.

## 6. Inspect Alerts

Prometheus alerts:

http://localhost:9090/alerts

Check alert state using:

```bash
curl -s http://localhost:9090/api/v1/alerts
```

Alertmanager:

http://localhost:9093

Compare alert timestamps with target health and application logs to help identify the cause.

## 7. Verify Recovery

After fixing the cause:

1. Confirm the API health endpoint returns HTTP 200.
2. Confirm the Kubernetes deployment and pod are Ready.
3. Confirm the Prometheus API target reports `up` and has no scrape error.
4. Confirm the alert is no longer firing.
5. Verify email notifications if expected.

Allow time for scrape and alert evaluation intervals before concluding that the issue is resolved.

## 8. Cost and Availability

If AKS was intentionally stopped to reduce costs, the API may be unavailable while the cluster is stopped.

Stopping AKS does not stop all Azure charges. Review other provisioned resources and their costs separately.

## Scope

This guide describes a development and portfolio environment. Production deployments require additional security hardening, HTTPS, appropriate network restrictions, and tested recovery procedures.