# PromptThread Python SDK

Git for prompts. Version control and performance tracking for AI prompts.

Part of the [Thread Suite](https://github.com/eugene001dayne/prompt-thread) — open-source reliability tools for AI agents.

## Installation
```bash
pip install promptthread
```

## Quick Start
```python
from promptthread import PromptThread

pt = PromptThread("https://prompt-thread.onrender.com")

# Create a prompt
prompt = pt.create_prompt(
    name="summarizer-v1",
    content="You are a summarizer. Return a 3-sentence summary.",
    description="First summarizer prompt",
    tags=["summarizer"]
)

prompt_id = prompt["id"]

# Log a run against it
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

# Get performance stats
stats = pt.get_stats(prompt_id)
print(stats)

# Update the prompt (creates new version automatically)
pt.update_prompt(
    prompt_id=prompt_id,
    content="You are a summarizer. Return a 2-sentence summary.",
)

# See what changed
diff = pt.diff(prompt_id, version_a=1, version_b=2)
print(diff)

# Roll back to version 1
pt.rollback(prompt_id, version=1)
```

## API Reference

### Prompts

| Method | Description |
|--------|-------------|
| `create_prompt(name, content, description, tags)` | Create a new prompt at version 1 |
| `list_prompts()` | List all prompts |
| `get_prompt(prompt_id)` | Get a prompt by ID |
| `update_prompt(prompt_id, content, description, tags)` | Update prompt, auto-increments version |
| `get_history(prompt_id)` | Get all previous versions |
| `rollback(prompt_id, version)` | Roll back to a previous version |
| `diff(prompt_id, version_a, version_b)` | Compare two versions |

### Runs

| Method | Description |
|--------|-------------|
| `log_run(prompt_id, prompt_version, ...)` | Log a run against a prompt version |
| `get_runs(prompt_id)` | Get all runs for a prompt |
| `get_stats(prompt_id)` | Get pass rate, latency, cost stats |
| `compare(prompt_id, version_a, version_b)` | Compare performance between versions |

## Part of the Thread Suite

| Tool | What it does |
|------|-------------|
| [Iron-Thread](https://github.com/eugene001dayne/iron-thread) | Validates AI output structure before it hits your database |
| [TestThread](https://github.com/eugene001dayne/test-thread) | Tests whether your agent behaves correctly across runs |
| **PromptThread** | Versions and tracks prompt performance over time |