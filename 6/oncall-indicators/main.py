import sys
from flask import Flask, jsonify, request
import os
import requests
import time
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("oncall-indicators")

app = Flask("oncall-indicators")

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

PROM_URL = getRequiredEnv("PROM_URL")
SAGE_TOKEN = getRequiredEnv("SAGE_TOKEN")
SAGE_SOURCE = getRequiredEnv("SAGE_SOURCE")
SAGE_GROUP = getRequiredEnv("SAGE_GROUP")
SAGE_SERVICE = getRequiredEnv("SAGE_SERVICE")
SLO_LATENCY = getRequiredEnv("SLO_LATENCY", float)
PROBE_TARGETS = [t.strip() for t in getRequiredEnv("PROBE_TARGETS").split(",") if t.strip()]

HEADERS = {
    "Authorization": f"Bearer {SAGE_TOKEN}",
    "Content-Type": "application/json",
    "accept": "*/*",
    "Source": SAGE_SOURCE,
}

def toIso(ts):
    return datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=3))).strftime(
        '%Y-%m-%dT%H:%M:%S.000+03:00'
    )

def querySage(pql, startTs, endTs, size=1000):
    body = {
        "query": pql,
        "size": size,
        "startTime": toIso(startTs),
        "endTime": toIso(endTs),
    }
    logger.info(f"Executing PQL query: {pql}")
    try:
        resp = requests.post(PROM_URL, json=body, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"Sage response: {data}")
        return data
    except requests.RequestException as e:
        logger.error(f"Sage request error: {e}")
        return {}

def extractLatestValue(data):
    hits = data.get("hits", [])
    if not hits:
        logger.warning("No data received (empty hits array).")
        return None
    hits_sorted = sorted(hits, key=lambda x: x.get("@timestamp", ""))
    latest = hits_sorted[-1]
    ts = latest.get("@timestamp")
    value = latest.get("value")
    logger.info(f"Latest value extracted: {value} (timestamp={ts})")
    return value

def averageProbeUp(target: str):
    now = int(time.time())
    pql = (
        f'pql step=1m (avg_over_time(probe_up{{group="{SAGE_GROUP}", '
        f'service="{SAGE_SERVICE}", target="{target}"}}[30m]) * 100)'
    )
    logger.info(f"Querying average_probe_up for {target}")
    data = querySage(pql, now, now)
    value = extractLatestValue(data)
    return float(value) if value is not None else None

def successRatio(target: str):
    now = int(time.time())
    pql = (
        f'pql (1 - (sum(rate(probe_request_errors_total{{group="{SAGE_GROUP}", '
        f'service="{SAGE_SERVICE}", target="{target}"}}[5m])) by (service, group, target) / '
        f'sum(rate(probe_requests_total{{group="{SAGE_GROUP}", service="{SAGE_SERVICE}", '
        f'target="{target}"}}[5m])) by (service, group, target))) * 100'
    )
    logger.info(f"Querying success_ratio for {target}")
    data = querySage(pql, now, now)
    value = extractLatestValue(data)
    return float(value) if value is not None else None

def calcLatencySla(avgLatency: float, slo: float) -> float:
    if avgLatency <= slo:
        return 100.0
    else:
        sla = 100 * slo / avgLatency
        return max(0.0, sla)

def latencySloRatio(target: str):
    now = int(time.time())
    start, end = now, now + 15
    pql = (
        f'pql last_over_time('
        f'histogram_quantile(0.99, sum(rate(probe_request_duration_seconds_bucket'
        f'{{group="{SAGE_GROUP}", service="{SAGE_SERVICE}", target="{target}"}}[5m])) by (le))'
        f'[1m:])'
    )
    logger.info(f"Querying latency_slo_ratio for {target}")
    data = querySage(pql, start, end)
    value = extractLatestValue(data)
    return calcLatencySla(float(value), SLO_LATENCY) if value is not None else None

def computeSLA(target):
    probe_up_avg = averageProbeUp(target)
    success = successRatio(target)
    latency_ratio = latencySloRatio(target)

    if probe_up_avg is None or success is None or latency_ratio is None:
        logger.warning(f"Insufficient data to compute SLA for {target}")
        return {
            "target": target,
            "error": "insufficient data",
            "probe_up_avg": probe_up_avg,
            "success_ratio": success,
            "latency_slo_ratio": latency_ratio,
            "sla_percent": None,
        }

    sla_value = (probe_up_avg + success + latency_ratio) / 3
    logger.info(f"SLA computed for {target}: {sla_value:.2f}%")
    return {
        "target": target,
        "probe_up_avg": probe_up_avg,
        "success_ratio": success,
        "latency_slo_ratio": latency_ratio,
        "sla_percent": round(sla_value, 2),
    }

@app.route("/sla")
def sla():
    logger.info("Computing SLA for all configured targets")
    minutes = int(request.args.get("minutes", "60"))
    results = []

    for target in PROBE_TARGETS:
        result = computeSLA(target)
        result["period_minutes"] = minutes
        results.append(result)

    return jsonify({"targets": results, "count": len(results)})


@app.route("/metrics")
def metrics():
    logger.info("Exporting SLA metrics for all configured targets")
    lines = []
    for target in PROBE_TARGETS:
        result = computeSLA(target)
        sla_value = result["sla_percent"] or 0
        lines.append(f'sla_percent{{target="{target}"}} {sla_value:.2f}')
    return "\n".join(lines) + "\n", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9200"))
    logger.info(f"Starting SLA service on port {port}")
    app.run(host="0.0.0.0", port=port)
