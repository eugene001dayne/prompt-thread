from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import prompts, runs
from app.routes import alerts
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="PromptThread",
    description="Git for prompts. Version control and performance tracking for AI prompts.",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

@app.get("/")
def root():
    return {
        "tool": "PromptThread",
        "version": "0.2.0",
        "status": "running",
        "description": "Git for prompts. Version control and performance tracking for AI prompts."
    }

@app.get("/health")
def health():
    return {"status": "ok"}