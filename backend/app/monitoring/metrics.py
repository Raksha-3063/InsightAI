import os
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# 1. Base API metrics
REQUEST_COUNT = Counter(
    "insightai_request_count_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "insightai_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

# 2. Domain metrics
MODEL_TRAINING_COUNT = Counter(
    "insightai_model_trainings_total",
    "Total machine learning model trainings triggered",
    ["algorithm", "task_type"]
)

FORECAST_TRAINING_COUNT = Counter(
    "insightai_forecast_trainings_total",
    "Total forecasting models trained",
    ["algorithm"]
)

AI_CHAT_COUNT = Counter(
    "insightai_ai_chat_requests_total",
    "Total AI Copilot messages sent"
)

# 3. System Metrics gauges
CPU_USAGE = Gauge(
    "insightai_system_cpu_usage_percent",
    "Current CPU usage percent of the host system"
)

MEMORY_USAGE = Gauge(
    "insightai_system_memory_usage_bytes",
    "Current RAM usage of the host system"
)

def update_system_gauges():
    """
    Updates Host CPU and memory gauge metrics.
    """
    try:
        CPU_USAGE.set(psutil.cpu_percent(interval=None))
        MEMORY_USAGE.set(psutil.virtual_memory().used)
    except Exception:
        pass

def expose_prometheus_metrics() -> Response:
    """
    Returns latest Prometheus scrape text response.
    """
    update_system_gauges()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
