# prompt-thread
Git for prompts + performance data. Let me think about the architecture quickly before giving the first instruction. Core entities:  Prompt - a named prompt (like a repo) PromptVersion - each commit (text, hash, metadata) PromptRun - each time a version is executed (latency, cost, pass/fail, output) ABTest - comparison between two versions
