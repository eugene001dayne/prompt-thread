from fastapi import APIRouter, HTTPException
from app.models import RunCreate
from app.database import get_client
from datetime import datetime, timezone

router = APIRouter()


@router.post("/")
def log_run(payload: RunCreate):
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "prompt_id": payload.prompt_id,
        "prompt_version": payload.prompt_version,
        "input": payload.input,
        "output": payload.output,
        "latency_ms": payload.latency_ms,
        "cost_usd": payload.cost_usd,
        "passed": payload.passed,
        "metadata": payload.metadata,
        "created_at": now
    }
    with get_client() as client:
        r = client.post("/runs", json=data)
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()[0]


@router.get("/")
def list_runs():
    with get_client() as client:
        r = client.get("/runs", params={"order": "created_at.desc"})
    return r.json()


@router.get("/{run_id}")
def get_run(run_id: str):
    with get_client() as client:
        r = client.get("/runs", params={"id": f"eq.{run_id}"})
    data = r.json()
    if not data:
        raise HTTPException(status_code=404, detail="Run not found.")
    return data[0]


@router.get("/prompt/{prompt_id}")
def get_runs_for_prompt(prompt_id: str):
    with get_client() as client:
        r = client.get("/runs", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "created_at.desc"
        })
    return r.json()


@router.get("/prompt/{prompt_id}/stats")
def get_prompt_stats(prompt_id: str):
    with get_client() as client:
        r = client.get("/runs", params={"prompt_id": f"eq.{prompt_id}"})
    runs = r.json()

    if not runs:
        return {"prompt_id": prompt_id, "total_runs": 0}

    total = len(runs)
    passed = sum(1 for r in runs if r.get("passed") is True)
    failed = sum(1 for r in runs if r.get("passed") is False)
    latencies = [r["latency_ms"] for r in runs if r.get("latency_ms") is not None]
    costs = [r["cost_usd"] for r in runs if r.get("cost_usd") is not None]

    return {
        "prompt_id": prompt_id,
        "total_runs": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else None,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "avg_cost_usd": round(sum(costs) / len(costs), 6) if costs else None,
    }


@router.get("/compare/{prompt_id}/{version_a}/{version_b}")
def compare_versions(prompt_id: str, version_a: int, version_b: int):
    def get_stats(version: int):
        with get_client() as client:
            r = client.get("/runs", params={
                "prompt_id": f"eq.{prompt_id}",
                "prompt_version": f"eq.{version}"
            })
        runs = r.json()
        total = len(runs)
        if total == 0:
            return {"version": version, "total_runs": 0}
        passed = sum(1 for r in runs if r.get("passed") is True)
        latencies = [r["latency_ms"] for r in runs if r.get("latency_ms") is not None]
        costs = [r["cost_usd"] for r in runs if r.get("cost_usd") is not None]
        return {
            "version": version,
            "total_runs": total,
            "passed": passed,
            "pass_rate": round(passed / total * 100, 2),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "avg_cost_usd": round(sum(costs) / len(costs), 6) if costs else None,
        }

    return {
        "prompt_id": prompt_id,
        "version_a": get_stats(version_a),
        "version_b": get_stats(version_b)
    }