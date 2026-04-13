import httpx
from typing import Optional, Dict, Any, List


class PromptThread:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url)

    # --- Prompts ---

    def create_prompt(self, name: str, content: str, description: str = None, tags: List[str] = []):
        r = self.client.post("/prompts/", json={
            "name": name,
            "content": content,
            "description": description,
            "tags": tags
        })
        r.raise_for_status()
        return r.json()

    def list_prompts(self):
        r = self.client.get("/prompts/")
        r.raise_for_status()
        return r.json()

    def get_prompt(self, prompt_id: str):
        r = self.client.get(f"/prompts/{prompt_id}")
        r.raise_for_status()
        return r.json()

    def update_prompt(self, prompt_id: str, content: str, description: str = None, tags: List[str] = []):
        r = self.client.put(f"/prompts/{prompt_id}", json={
            "content": content,
            "description": description,
            "tags": tags
        })
        r.raise_for_status()
        return r.json()

    def get_history(self, prompt_id: str):
        r = self.client.get(f"/prompts/{prompt_id}/history")
        r.raise_for_status()
        return r.json()

    def rollback(self, prompt_id: str, version: int):
        r = self.client.post(f"/prompts/{prompt_id}/rollback/{version}")
        r.raise_for_status()
        return r.json()

    def diff(self, prompt_id: str, version_a: int, version_b: int):
        r = self.client.get(f"/prompts/{prompt_id}/diff/{version_a}/{version_b}")
        r.raise_for_status()
        return r.json()

    # --- Runs ---

    def log_run(self, prompt_id: str, prompt_version: int, input: str = None,
                output: str = None, latency_ms: float = None, cost_usd: float = None,
                passed: bool = None, metadata: Dict[str, Any] = {}):
        r = self.client.post("/runs/", json={
            "prompt_id": prompt_id,
            "prompt_version": prompt_version,
            "input": input,
            "output": output,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "passed": passed,
            "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def get_runs(self, prompt_id: str):
        r = self.client.get(f"/runs/prompt/{prompt_id}")
        r.raise_for_status()
        return r.json()

    def get_stats(self, prompt_id: str):
        r = self.client.get(f"/runs/prompt/{prompt_id}/stats")
        r.raise_for_status()
        return r.json()

    def compare(self, prompt_id: str, version_a: int, version_b: int):
        r = self.client.get(f"/runs/compare/{prompt_id}/{version_a}/{version_b}")
        r.raise_for_status()
        return r.json()

    # --- Drift ---

    def create_drift_anchor(self, prompt_id: str, name: str, input: str,
                             expected_contains: str, model_endpoint: str):
        r = self.client.post("/drift/anchors", json={
            "prompt_id": prompt_id,
            "name": name,
            "input": input,
            "expected_contains": expected_contains,
            "model_endpoint": model_endpoint
        })
        r.raise_for_status()
        return r.json()

    def list_drift_anchors(self, prompt_id: str):
        r = self.client.get(f"/drift/anchors/{prompt_id}")
        r.raise_for_status()
        return r.json()

    def run_drift_check(self, prompt_id: str):
        r = self.client.post(f"/drift/anchors/{prompt_id}/check")
        r.raise_for_status()
        return r.json()

    def drift_history(self, prompt_id: str):
        r = self.client.get(f"/drift/{prompt_id}/history")
        r.raise_for_status()
        return r.json()