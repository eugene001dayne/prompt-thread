from fastapi import APIRouter, HTTPException
from app.database import get_client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import httpx

router = APIRouter()


class DriftAnchorCreate(BaseModel):
    prompt_id: str
    name: str
    input: str
    expected_contains: str
    model_endpoint: str


class AnchorResult(BaseModel):
    anchor_id: str
    name: str
    input: str
    expected_contains: str
    actual_output: str
    passed: bool
    previously_passed: Optional[bool] = None
    newly_failing: bool = False


@router.post("/anchors")
def create_drift_anchor(payload: DriftAnchorCreate):
    now = datetime.now(timezone.utc).isoformat()
    with get_client() as client:
        r = client.post("/drift_anchors", json={
            "prompt_id": payload.prompt_id,
            "name": payload.name,
            "input": payload.input,
            "expected_contains": payload.expected_contains,
            "model_endpoint": payload.model_endpoint,
            "created_at": now
        })
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()[0]


@router.get("/anchors/{prompt_id}")
def list_drift_anchors(prompt_id: str):
    with get_client() as client:
        r = client.get("/drift_anchors", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "created_at.asc"
        })
    return r.json()


@router.post("/anchors/{prompt_id}/check")
def run_drift_check(prompt_id: str):
    with get_client() as client:
        anchors_r = client.get("/drift_anchors", params={
            "prompt_id": f"eq.{prompt_id}"
        })
    anchors = anchors_r.json()

    if not anchors:
        raise HTTPException(status_code=404, detail="No drift anchors found for this prompt.")

    now = datetime.now(timezone.utc).isoformat()
    results = []
    passed_count = 0
    failed_count = 0
    drift_detected = False

    for anchor in anchors:
        actual_output = ""
        try:
            resp = httpx.post(
                anchor["model_endpoint"],
                json={"input": anchor["input"]},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                actual_output = data.get("output", data.get("response", data.get("result", str(data))))
            else:
                actual_output = f"[Error: HTTP {resp.status_code}]"
        except Exception as e:
            actual_output = f"[Error: {str(e)}]"

        passed = anchor["expected_contains"].lower() in actual_output.lower()
        previously_passed = anchor.get("last_passed")
        newly_failing = (previously_passed is True) and (not passed)

        if newly_failing:
            drift_detected = True

        if passed:
            passed_count += 1
        else:
            failed_count += 1

        result = {
            "anchor_id": anchor["id"],
            "name": anchor["name"],
            "input": anchor["input"],
            "expected_contains": anchor["expected_contains"],
            "actual_output": actual_output,
            "passed": passed,
            "previously_passed": previously_passed,
            "newly_failing": newly_failing
        }
        results.append(result)

        with get_client() as client:
            client.patch(
                "/drift_anchors",
                params={"id": f"eq.{anchor['id']}"},
                json={
                    "last_checked_at": now,
                    "last_passed": passed
                }
            )

    with get_client() as client:
        client.post("/drift_check_runs", json={
            "prompt_id": prompt_id,
            "checked_at": now,
            "total_anchors": len(anchors),
            "passed": passed_count,
            "failed": failed_count,
            "drift_detected": drift_detected,
            "results": results
        })

    return {
        "prompt_id": prompt_id,
        "checked_at": now,
        "total_anchors": len(anchors),
        "passed": passed_count,
        "failed": failed_count,
        "drift_detected": drift_detected,
        "results": results
    }


@router.get("/{prompt_id}/history")
def get_drift_history(prompt_id: str):
    with get_client() as client:
        r = client.get("/drift_check_runs", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "checked_at.desc"
        })
    runs = r.json()

    return {
        "prompt_id": prompt_id,
        "total_runs": len(runs),
        "drift_detected_count": sum(1 for run in runs if run.get("drift_detected")),
        "history": runs
    }