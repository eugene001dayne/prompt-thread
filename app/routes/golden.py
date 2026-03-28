from fastapi import APIRouter, HTTPException
from app.database import get_client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

router = APIRouter()


class GoldenCaseCreate(BaseModel):
    prompt_id: str
    name: str
    input: str
    expected_output: Optional[str] = None
    expected_contains: Optional[str] = None
    must_pass: Optional[bool] = True


class GoldenCaseResult(BaseModel):
    golden_id: str
    actual_output: str
    passed: bool


@router.post("/")
def create_golden_case(payload: GoldenCaseCreate):
    now = datetime.now(timezone.utc).isoformat()
    with get_client() as client:
        r = client.post("/golden_sets", json={
            "prompt_id": payload.prompt_id,
            "name": payload.name,
            "input": payload.input,
            "expected_output": payload.expected_output,
            "expected_contains": payload.expected_contains,
            "must_pass": payload.must_pass,
            "created_at": now
        })
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()[0]


@router.get("/{prompt_id}")
def get_golden_cases(prompt_id: str):
    with get_client() as client:
        r = client.get("/golden_sets", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "created_at.desc"
        })
    return r.json()


@router.delete("/{golden_id}")
def delete_golden_case(golden_id: str):
    with get_client() as client:
        r = client.delete("/golden_sets", params={"id": f"eq.{golden_id}"})
    return {"deleted": golden_id}


@router.post("/{prompt_id}/run")
def run_golden_set(prompt_id: str, results: list[GoldenCaseResult]):
    with get_client() as client:
        cases = client.get("/golden_sets", params={
            "prompt_id": f"eq.{prompt_id}"
        }).json()

    if not cases:
        raise HTTPException(status_code=404, detail="No golden cases found for this prompt.")

    results_map = {r.golden_id: r for r in results}
    now = datetime.now(timezone.utc).isoformat()

    summary = []
    total = 0
    passed = 0

    for case in cases:
        result = results_map.get(case["id"])
        if not result:
            continue

        actual_passed = result.passed

        if case.get("expected_contains"):
            actual_passed = case["expected_contains"].lower() in result.actual_output.lower()
        elif case.get("expected_output"):
            actual_passed = result.actual_output.strip() == case["expected_output"].strip()

        with get_client() as client:
            client.patch("/golden_sets", params={"id": f"eq.{case['id']}"}, json={
                "last_run_passed": actual_passed,
                "last_run_at": now
            })

        total += 1
        if actual_passed:
            passed += 1

        summary.append({
            "golden_id": case["id"],
            "name": case["name"],
            "passed": actual_passed,
            "must_pass": case["must_pass"],
            "actual_output": result.actual_output
        })

    failed_required = [s for s in summary if not s["passed"] and s["must_pass"]]

    return {
        "prompt_id": prompt_id,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else None,
        "regression_detected": len(failed_required) > 0,
        "failed_required_cases": failed_required,
        "results": summary
    }


def run_golden_set_on_update(prompt_id: str):
    with get_client() as client:
        cases = client.get("/golden_sets", params={
            "prompt_id": f"eq.{prompt_id}",
            "must_pass": "eq.true"
        }).json()

    if not cases:
        return None

    return {
        "message": f"{len(cases)} golden cases exist for this prompt. Run POST /golden/{prompt_id}/run to validate the new version.",
        "golden_count": len(cases),
        "prompt_id": prompt_id
    }