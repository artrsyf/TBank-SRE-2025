import aiohttp
import asyncio
import os, sys, time, logging
from prometheus_client import start_http_server, Gauge, Histogram, Counter

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger("oncall-prober")

def getRequiredEnv(name: str, cast=str):
    envValue = os.environ.get(name)
    if envValue is None or envValue.strip() == "":
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    try:
        return cast(envValue)
    except Exception as e:
        logger.error(f"Invalid value for {name}: {e}")
        sys.exit(1)

TARGETS = getRequiredEnv("PROBE_TARGETS").split(",")
INTERVAL = getRequiredEnv("PROBE_INTERVAL", int)
PORT = getRequiredEnv("METRICS_PORT", int)
TIMEOUT = getRequiredEnv("PROBE_TIMEOUT", int)

requestsTotal = Counter(
    "probe_requests_total",
    "Total HTTP probe requests sent",
    ["target"]
)

requestErrorsTotal = Counter(
    "probe_request_errors_total",
    "Total failed HTTP probe requests (non-2xx or timeout)",
    ["target"]
)

requestDurationSeconds = Histogram(
    "probe_request_duration_seconds",
    "HTTP request latency in seconds",
    ["target"]
)

probeUp = Gauge(
    "probe_up",
    "1 if last probe succeeded (2xx), else 0",
    ["target"]
)

async def probeTarget(session: aiohttp.ClientSession, target: str):
    requestsTotal.labels(target=target).inc()
    startTime = time.time()

    def processFailure():
        probeUp.labels(target=target).set(0)
        requestErrorsTotal.labels(target=target).inc()

    try:
        async with session.get(target, timeout=TIMEOUT) as response:
            latency = time.time() - startTime
            requestDurationSeconds.labels(target=target).observe(latency)

            if 200 <= response.status < 300:
                probeUp.labels(target=target).set(1)
                logger.info(f"Probe success | target={target} | status={response.status} | latency={latency:.3f}s")
            else:
                processFailure()
                logger.warning(f"Probe failed | target={target} | HTTP status {response.status}")

    except asyncio.TimeoutError:
        processFailure()
        logger.warning(f"Probe failed | target={target} | timeout after {TIMEOUT}s")

    except Exception as e:
        processFailure()
        logger.warning(f"Probe failed | target={target} | exception: {e}")

async def proberLoop():
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [probeTarget(session, t.strip()) for t in TARGETS if t.strip()]
            await asyncio.gather(*tasks)
            await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    logger.info("Starting HTTP probe exporter")
    logger.info(f"Listening on :{PORT}")
    logger.info(f"Targets: {TARGETS}")
    logger.info(f"Interval={INTERVAL}s | Timeout={TIMEOUT}s | LogLevel={LOG_LEVEL}")

    start_http_server(PORT)
    asyncio.run(proberLoop())