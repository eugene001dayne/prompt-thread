const fetch = require("node-fetch");

class PromptThread {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async _request(method, path, body = null) {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${this.baseUrl}${path}`, options);
    if (!res.ok) throw new Error(`PromptThread error: ${res.status} ${await res.text()}`);
    return res.json();
  }

  // --- Prompts ---
  createPrompt(name, content, description = null, tags = []) {
    return this._request("POST", "/prompts/", { name, content, description, tags });
  }

  listPrompts() {
    return this._request("GET", "/prompts/");
  }

  getPrompt(promptId) {
    return this._request("GET", `/prompts/${promptId}`);
  }

  updatePrompt(promptId, content, description = null, tags = []) {
    return this._request("PUT", `/prompts/${promptId}`, { content, description, tags });
  }

  getHistory(promptId) {
    return this._request("GET", `/prompts/${promptId}/history`);
  }

  rollback(promptId, version) {
    return this._request("POST", `/prompts/${promptId}/rollback/${version}`);
  }

  diff(promptId, versionA, versionB) {
    return this._request("GET", `/prompts/${promptId}/diff/${versionA}/${versionB}`);
  }

  // --- Runs ---
  logRun(promptId, promptVersion, { input, output, latencyMs, costUsd, passed, metadata } = {}) {
    return this._request("POST", "/runs/", {
      prompt_id: promptId,
      prompt_version: promptVersion,
      input,
      output,
      latency_ms: latencyMs,
      cost_usd: costUsd,
      passed,
      metadata: metadata || {}
    });
  }

  getRuns(promptId) {
    return this._request("GET", `/runs/prompt/${promptId}`);
  }

  getStats(promptId) {
    return this._request("GET", `/runs/prompt/${promptId}/stats`);
  }

  compare(promptId, versionA, versionB) {
    return this._request("GET", `/runs/compare/${promptId}/${versionA}/${versionB}`);
  }

  // --- Drift ---
  createDriftAnchor(promptId, name, input, expectedContains, modelEndpoint) {
    return this._request("POST", "/drift/anchors", {
      prompt_id: promptId,
      name,
      input,
      expected_contains: expectedContains,
      model_endpoint: modelEndpoint
    });
  }

  listDriftAnchors(promptId) {
    return this._request("GET", `/drift/anchors/${promptId}`);
  }

  runDriftCheck(promptId) {
    return this._request("POST", `/drift/anchors/${promptId}/check`);
  }

  driftHistory(promptId) {
    return this._request("GET", `/drift/${promptId}/history`);
  }
}

module.exports = PromptThread;