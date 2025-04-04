from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_client.openmetrics.exposition import generate_latest
from fastapi import Response
import psutil

# API Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# System Metrics
CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'memory_usage_megabytes',
    'Memory usage in megabytes'
)

DISK_USAGE = Gauge(
    'disk_usage_percent',
    'Disk usage percentage'
)

# Custom Metrics
AUTH_FAILURES = Counter(
    'auth_failures_total',
    'Total number of authentication failures'
)

ORDER_COUNT = Counter(
    'orders_total',
    'Total number of orders',
    ['status']
)

def update_system_metrics():
    """Update system metrics periodically"""
    CPU_USAGE.set(psutil.cpu_percent())
    # Convert bytes to megabytes
    memory_mb = psutil.virtual_memory().used / (1024 * 1024)
    MEMORY_USAGE.set(memory_mb)
    DISK_USAGE.set(psutil.disk_usage('/').percent)

async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    update_system_metrics()
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """Record request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def record_auth_failure():
    """Record authentication failure"""
    AUTH_FAILURES.inc()

def record_order(status: str):
    """Record new order"""
    ORDER_COUNT.labels(status=status).inc() 