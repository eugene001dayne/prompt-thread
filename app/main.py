from fastapi import FastAPI
from app.routes import prompts, runs
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="PromptThread",
    description="Git for prompts. Version control and performance tracking for AI prompts.",
    version="0.1.0"
)

app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])

@app.get("/")
def root():
    return {
        "tool": "PromptThread",
        "version": "0.1.0",
        "status": "running",
        "description": "Git for prompts. Version control and performance tracking for AI prompts."
    }

@app.get("/health")
def health():
    return {"status": "ok"}