# PromptThread JavaScript SDK

Git for prompts. Version control and performance tracking for AI prompts.

Part of the [Thread Suite](https://github.com/eugene001dayne/prompt-thread) — open-source reliability tools for AI agents.

## Installation
```bash
npm install promptthread
```

## Quick Start
```javascript
const PromptThread = require("promptthread");

const pt = new PromptThread("https://prompt-thread.onrender.com");

async function main() {
  // Create a prompt
  const prompt = await pt.createPrompt(
    "summarizer-v1",
    "You are a summarizer. Return a 3-sentence summary.",
    "First summarizer prompt",
    ["summarizer"]
  );

  const promptId = prompt.id;

  // Log a run against it
  await pt.logRun(promptId, 1, {
    input: "Long text here...",
    output: "Summary here...",
    latencyMs: 340.5,
    costUsd: 0.000021,
    passed: true,
    metadata: { model: "gpt-4o" }
  });

  // Get performance stats
  const stats = await pt.getStats(promptId);
  console.log(stats);

  // Update the prompt (creates new version automatically)
  await pt.updatePrompt(
    promptId,
    "You are a summarizer. Return a 2-sentence summary."
  );

  // See what changed
  const diff = await pt.diff(promptId, 1, 2);
  console.log(diff);

  // Roll back to version 1
  await pt.rollback(promptId, 1);
}

main();
```

## API Reference

### Prompts

| Method | Description |
|--------|-------------|
| `createPrompt(name, content, description, tags)` | Create a new prompt at version 1 |
| `listPrompts()` | List all prompts |
| `getPrompt(promptId)` | Get a prompt by ID |
| `updatePrompt(promptId, content, description, tags)` | Update prompt, auto-increments version |
| `getHistory(promptId)` | Get all previous versions |
| `rollback(promptId, version)` | Roll back to a previous version |
| `diff(promptId, versionA, versionB)` | Compare two versions |

### Runs

| Method | Description |
|--------|-------------|
| `logRun(promptId, promptVersion, options)` | Log a run against a prompt version |
| `getRuns(promptId)` | Get all runs for a prompt |
| `getStats(promptId)` | Get pass rate, latency, cost stats |
| `compare(promptId, versionA, versionB)` | Compare performance between versions |

## Part of the Thread Suite

| Tool | What it does |
|------|-------------|
| [Iron-Thread](https://github.com/eugene001dayne/iron-thread) | Validates AI output structure before it hits your database |
| [TestThread](https://github.com/eugene001dayne/test-thread) | Tests whether your agent behaves correctly across runs |
| **PromptThread** | Versions and tracks prompt performance over time |