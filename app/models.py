from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# --- Prompt Models ---

class PromptCreate(BaseModel):
    name: str
    content: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []


class PromptUpdate(BaseModel):
    content: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []


# --- Run Models ---

class RunCreate(BaseModel):
    prompt_id: str
    prompt_version: int
    input: Optional[str] = None
    output: Optional[str] = None
    latency_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    passed: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = {}


# --- Response Models ---

class PromptResponse(BaseModel):
    id: str
    name: str
    content: str
    version: int
    description: Optional[str] = None
    tags: Optional[list[str]] = []
    created_at: datetime
    updated_at: datetime


class RunResponse(BaseModel):
    id: str
    prompt_id: str
    prompt_version: int
    input: Optional[str] = None
    output: Optional[str] = None
    latency_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    passed: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime