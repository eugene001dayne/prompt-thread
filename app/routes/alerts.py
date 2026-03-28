from fastapi import APIRouter, HTTPException
from app.database import get_client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import httpx

router = APIRouter()


class AlertConfigCreate(BaseModel):
    prompt_id: str
    min_pass_rate: Optional[float] = 80.0
    max_latency_ms: Optional[float] = 2000.0
    max_cost_usd: Optional[float] = 0.01
    webhook_url: Optional[str] = None
    active: Optional[bool] = True


@router.post("/config")
def create_alert_config(payload: AlertConfigCreate):
    now = datetime.now(timezone.utc).isoformat()
    with get_client() as client:
        r = client.post("/alert_configs", json={
            "prompt_id": payload.prompt_id,
            "min_pass_rate": payload.min_pass_rate,
            "max_latency_ms": payload.max_latency_ms,
            "max_cost_usd": payload.max_cost_usd,
            "webhook_url": payload.webhook_url,
            "active": payload.active,
            "created_at": now
        })
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()[0]


@router.get("/config/{prompt_id}")
def get_alert_config(prompt_id: str):
    with get_client() as client:
        r = client.get("/alert_configs", params={"prompt_id": f"eq.{prompt_id}"})
    data = r.json()
    if not data:
        raise HTTPException(status_code=404, detail="No alert config found for this prompt.")
    return data[0]


@router.get("/{prompt_id}")
def get_alerts(prompt_id: str):
    with get_client() as client:
        r = client.get("/alerts", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "created_at.desc"
        })
    return r.json()


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    with get_client() as client:
        r = client.patch("/alerts", params={"id": f"eq.{alert_id}"}, json={"resolved": True})
    if not r.json():
        raise HTTPException(status_code=404, detail="Alert not found.")
    return r.json()[0]


def check_and_fire_alerts(prompt_id: str, prompt_version: int):
    with get_client() as client:
        config_r = client.get("/alert_configs", params={
            "prompt_id": f"eq.{prompt_id}",
            "active": "eq.true"
        })
    configs = config_r.json()
    if not configs:
        return

    config = configs[0]

    with get_client() as client:
        runs_r = client.get("/runs", params={
            "prompt_id": f"eq.{prompt_id}",
            "prompt_version": f"eq.{prompt_version}"
        })
    runs = runs_r.json()

    if len(runs) < 3:
        return

    total = len(runs)
    passed = sum(1 for r in runs if r.get("passed") is True)
    pass_rate = round(passed / total * 100, 2)
    latencies = [r["latency_ms"] for r in runs if r.get("latency_ms") is not None]
    costs = [r["cost_usd"] for r in runs if r.get("cost_usd") is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None
    avg_cost = round(sum(costs) / len(costs), 6) if costs else None

    fired = []

    if pass_rate < config["min_pass_rate"]:
        fired.append({
            "alert_type": "low_pass_rate",
            "message": f"Pass rate dropped to {pass_rate}% (threshold: {config['min_pass_rate']}%)",
            "current_value": pass_rate,
            "threshold_value": config["min_pass_rate"]
        })

    if avg_latency and avg_latency > config["max_latency_ms"]:
        fired.append({
            "alert_type": "high_latency",
            "message": f"Avg latency spiked to {avg_latency}ms (threshold: {config['max_latency_ms']}ms)",
            "current_value": avg_latency,
            "threshold_value": config["max_latency_ms"]
        })

    if avg_cost and avg_cost > config["max_cost_usd"]:
        fired.append({
            "alert_type": "high_cost",
            "message": f"Avg cost rose to ${avg_cost} (threshold: ${config['max_cost_usd']})",
            "current_value": avg_cost,
            "threshold_value": config["max_cost_usd"]
        })

    now = datetime.now(timezone.utc).isoformat()
    for alert in fired:
        with get_client() as client:
            client.post("/alerts", json={
                "prompt_id": prompt_id,
                "prompt_version": prompt_version,
                **alert,
                "resolved": False,
                "created_at": now
            })

        if config.get("webhook_url") and fired:
            try:
                httpx.post(config["webhook_url"], json={
                    "tool": "PromptThread",
                    "prompt_id": prompt_id,
                    "prompt_version": prompt_version,
                    **alert
                }, timeout=5)
            except Exception:
                pass