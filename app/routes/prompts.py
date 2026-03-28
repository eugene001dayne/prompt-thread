from fastapi import APIRouter, HTTPException
from app.models import PromptCreate, PromptUpdate
from app.database import get_client
from datetime import datetime, timezone

router = APIRouter()


@router.post("/")
def create_prompt(payload: PromptCreate):
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "name": payload.name,
        "content": payload.content,
        "description": payload.description,
        "tags": payload.tags,
        "version": 1,
        "created_at": now,
        "updated_at": now
    }
    with get_client() as client:
        r = client.post("/prompts", json=data)
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()[0]


@router.get("/")
def list_prompts():
    with get_client() as client:
        r = client.get("/prompts", params={"order": "created_at.desc"})
    return r.json()


@router.get("/{prompt_id}")
def get_prompt(prompt_id: str):
    with get_client() as client:
        r = client.get("/prompts", params={"id": f"eq.{prompt_id}"})
    data = r.json()
    if not data:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    return data[0]


@router.put("/{prompt_id}")
def update_prompt(prompt_id: str, payload: PromptUpdate):
    with get_client() as client:
        existing = client.get("/prompts", params={"id": f"eq.{prompt_id}"})
    data = existing.json()
    if not data:
        raise HTTPException(status_code=404, detail="Prompt not found.")

    current = data[0]
    old_version = {k: v for k, v in current.items() if k != "id"}

    with get_client() as client:
        client.post("/prompt_history", json={
            **old_version,
            "prompt_id": prompt_id,
            "archived_at": datetime.now(timezone.utc).isoformat()
        })

    new_version = current["version"] + 1
    now = datetime.now(timezone.utc).isoformat()

    with get_client() as client:
        r = client.patch("/prompts", params={"id": f"eq.{prompt_id}"}, json={
            "content": payload.content,
            "description": payload.description,
            "tags": payload.tags,
            "version": new_version,
            "updated_at": now
        })
    return r.json()[0]


@router.get("/{prompt_id}/history")
def get_prompt_history(prompt_id: str):
    with get_client() as client:
        r = client.get("/prompt_history", params={
            "prompt_id": f"eq.{prompt_id}",
            "order": "version.desc"
        })
    return r.json()


@router.post("/{prompt_id}/rollback/{version}")
def rollback_prompt(prompt_id: str, version: int):
    with get_client() as client:
        history = client.get("/prompt_history", params={
            "prompt_id": f"eq.{prompt_id}",
            "version": f"eq.{version}"
        })
    if not history.json():
        raise HTTPException(status_code=404, detail="Version not found in history.")

    target = history.json()[0]

    with get_client() as client:
        current = client.get("/prompts", params={"id": f"eq.{prompt_id}"})
    if not current.json():
        raise HTTPException(status_code=404, detail="Prompt not found.")

    current_data = current.json()[0]
    old_version = {k: v for k, v in current_data.items() if k != "id"}

    with get_client() as client:
        client.post("/prompt_history", json={
            **old_version,
            "prompt_id": prompt_id,
            "archived_at": datetime.now(timezone.utc).isoformat()
        })

    new_version = current_data["version"] + 1
    now = datetime.now(timezone.utc).isoformat()

    with get_client() as client:
        r = client.patch("/prompts", params={"id": f"eq.{prompt_id}"}, json={
            "content": target["content"],
            "description": target["description"],
            "tags": target["tags"],
            "version": new_version,
            "updated_at": now
        })

    return {"message": f"Rolled back to version {version}. Now at version {new_version}.", "prompt": r.json()[0]}


@router.get("/{prompt_id}/diff/{version_a}/{version_b}")
def diff_versions(prompt_id: str, version_a: int, version_b: int):
    with get_client() as client:
        history = client.get("/prompt_history", params={"prompt_id": f"eq.{prompt_id}"})
        current = client.get("/prompts", params={"id": f"eq.{prompt_id}"})

    all_data = history.json() + current.json()
    va = next((v for v in all_data if v.get("version") == version_a), None)
    vb = next((v for v in all_data if v.get("version") == version_b), None)

    if not va or not vb:
        raise HTTPException(status_code=404, detail="One or both versions not found.")

    return {
        "prompt_id": prompt_id,
        "version_a": {"version": version_a, "content": va["content"]},
        "version_b": {"version": version_b, "content": vb["content"]},
    }