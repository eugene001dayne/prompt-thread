# PromptThread

**Git for prompts. Version control and performance tracking for AI prompts.**

Part of the [Thread Suite](https://github.com/eugene001dayne) — open-source reliability tools for AI agents.

[![PyPI version](https://badge.fury.io/py/promptthread.svg)](https://pypi.org/project/promptthread/)
[![npm version](https://badge.fury.io/js/promptthread.svg)](https://www.npmjs.com/package/promptthread)

---

## The Problem

When a developer changes a prompt, what broke? What improved? Which version performed best?

Right now there's no clean answer. Developers change prompts and hope for the best.

**PromptThread fixes that.**

---

## What It Does

- **Version control** — every prompt change is saved, like Git commits
- **Performance tracking** — pass rate, latency, and cost per version
- **A/B comparison** — which version actually performed better?
- **Rollback** — instantly restore any previous version
- **Diff view** — see exactly what changed between versions

---

## Quick Start

### Python
```bash
pip install promptthread
```
```python
from promptthread import PromptThread

pt = PromptThread("https://prompt-thread.onrender.com")

# Create a prompt
prompt = pt.create_prompt(
    name="summarizer-v1",
    content="You are a summarizer. Return a 3-sentence summary.",
    tags=["summarizer"]
)

prompt_id = prompt["id"]

# Log a run
pt.log_run(
    prompt_id=prompt_id,
    prompt_version=1,
    input="Long text here...",
    output="Summary here...",
    latency_ms=340.5,
    cost_usd=0.000021,
    passed=True,
    metadata={"model": "gpt-4o"}
)

# Get stats
print(pt.get_stats(prompt_id))

# Update prompt — auto-increments version
pt.update_prompt(prompt_id, "You are a summarizer. Return a 2-sentence summary.")

# See what changed
print(pt.diff(prompt_id, 1, 2))

# Roll back
pt.rollback(prompt_id, version=1)
```

### JavaScript
```bash
npm install promptthread
```
```javascript
const PromptThread = require("promptthread");

const pt = new PromptThread("https://prompt-thread.onrender.com");

const prompt = await pt.createPrompt(
  "summarizer-v1",
  "You are a summarizer. Return a 3-sentence summary.",
  "First version",
  ["summarizer"]
);

await pt.logRun(prompt.id, 1, {
  input: "Long text here...",
  output: "Summary here...",
  latencyMs: 340.5,
  costUsd: 0.000021,
  passed: true,
  metadata: { model: "gpt-4o" }
});

console.log(await pt.getStats(prompt.id));
```

---

## API Reference

**Base URL:** `https://prompt-thread.onrender.com`

**Interactive docs:** `https://prompt-thread.onrender.com/docs`

### Prompts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/prompts/` | POST | Create a new prompt |
| `/prompts/` | GET | List all prompts |
| `/prompts/{id}` | GET | Get a prompt by ID |
| `/prompts/{id}` | PUT | Update prompt, auto-increments version |
| `/prompts/{id}/history` | GET | Get all previous versions |
| `/prompts/{id}/rollback/{version}` | POST | Roll back to a version |
| `/prompts/{id}/diff/{v1}/{v2}` | GET | Compare two versions |

### Runs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/runs/` | POST | Log a run |
| `/runs/prompt/{id}` | GET | Get all runs for a prompt |
| `/runs/prompt/{id}/stats` | GET | Get pass rate, latency, cost |
| `/runs/compare/{id}/{v1}/{v2}` | GET | Compare versions by performance |

---

## The Thread Suite

Three open-source tools that together form the reliability layer for AI agents.

| Tool | What it does |
|------|-------------|
| [Iron-Thread](https://github.com/eugene001dayne/iron-thread) | Validates AI output structure before it hits your database |
| [TestThread](https://github.com/eugene001dayne/test-thread) | Tests whether your agent behaves correctly across runs |
| **PromptThread** | Versions and tracks prompt performance over time |

---

## Self-Hosting
```bash
git clone https://github.com/eugene001dayne/prompt-thread.git
cd prompt-thread
pip install -r requirements.txt
cp .env.example .env
# Add your SUPABASE_URL and SUPABASE_KEY to .env
python -m uvicorn app.main:app --reload
```

---

## License

MIT