#!/usr/bin/env node
// Call real Jev MCP tools (@jkudish/jev-mcp over stdio) and keep an immutable receipt per call.
//
//   node tools/jev_call.mjs --run RUN_DIR --id DECISION_ID --tool jev_decide --args args.json [--purpose "..."] [--evidence-file path ...]
//
// RUN_DIR is created if missing; each call writes RUN_DIR/<id>.json holding the exact request, the full
// MCP result, SHA-256 of every named evidence file, wall time, and server/model identity. An existing
// receipt is never overwritten. The API key is read from the environment and never written.
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({
  options: {
    run: { type: "string" },
    id: { type: "string" },
    tool: { type: "string" },
    args: { type: "string" },
    purpose: { type: "string", default: "" },
    "evidence-file": { type: "string", multiple: true, default: [] },
    server: { type: "string", default: process.env.JEV_MCP_BIN ?? "" },
    timeout: { type: "string", default: "180000" },
  },
});
for (const key of ["run", "id", "tool", "args"]) {
  if (!values[key]) {
    console.error(`missing --${key}`);
    process.exit(2);
  }
}
if (!/^[A-Za-z0-9._-]+$/.test(values.id)) {
  console.error("--id must be a stable slug");
  process.exit(2);
}

const runDir = resolve(values.run);
mkdirSync(runDir, { recursive: true });
const receiptPath = join(runDir, `${values.id}.json`);
if (existsSync(receiptPath)) {
  console.error(`receipt exists, not overwriting: ${receiptPath}`);
  process.exit(2);
}

const sha256 = (buffer) => createHash("sha256").update(buffer).digest("hex");
const toolArgs = JSON.parse(readFileSync(values.args, "utf8"));
const argsBytes = readFileSync(values.args);
const evidenceFiles = values["evidence-file"].map((path) => ({ path, sha256: sha256(readFileSync(path)), bytes: readFileSync(path).length }));

const serverArgs = values.server ? [values.server] : ["-y", "@jkudish/jev-mcp"];
const command = values.server ? process.execPath : "npx";
const env = { ...process.env, JEV_MCP_MODEL: process.env.JEV_MCP_MODEL ?? "typesafe/jev-1.13" };
const child = spawn(command, serverArgs, { env, stdio: ["pipe", "pipe", "pipe"] });
let stderr = "";
child.stderr.on("data", (chunk) => (stderr += chunk));

const pending = new Map();
let buffer = "";
child.stdout.on("data", (chunk) => {
  buffer += chunk;
  let newline;
  while ((newline = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, newline).trim();
    buffer = buffer.slice(newline + 1);
    if (!line) continue;
    const message = JSON.parse(line);
    if (message.id !== undefined && pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  }
});
let nextId = 1;
const rpc = (method, params) =>
  new Promise((resolvePromise, reject) => {
    const id = nextId++;
    const timer = setTimeout(() => reject(new Error(`timeout on ${method}`)), Number(values.timeout));
    pending.set(id, (message) => {
      clearTimeout(timer);
      resolvePromise(message);
    });
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  });

const started = Date.now();
let receipt;
try {
  const init = await rpc("initialize", {
    protocolVersion: "2025-06-18",
    capabilities: {},
    clientInfo: { name: "fr2-jev-ledger", version: "1" },
  });
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  const call = await rpc("tools/call", { name: values.tool, arguments: toolArgs });
  receipt = {
    id: values.id,
    purpose: values.purpose,
    tool: values.tool,
    server: init.result?.serverInfo ?? null,
    model: env.JEV_MCP_MODEL,
    provider_env: env.TYPESAFE_API_KEY ? "typesafe" : env.OPENROUTER_API_KEY ? "openrouter" : "none",
    args_file: values.args,
    args_sha256: sha256(argsBytes),
    arguments: toolArgs,
    evidence_files: evidenceFiles,
    started_utc: new Date(started).toISOString(),
    seconds: (Date.now() - started) / 1000,
    rpc_error: call.error ?? null,
    is_error: call.result?.isError ?? false,
    result: call.result ?? null,
  };
} catch (error) {
  receipt = {
    id: values.id,
    purpose: values.purpose,
    tool: values.tool,
    arguments: toolArgs,
    args_sha256: sha256(argsBytes),
    evidence_files: evidenceFiles,
    started_utc: new Date(started).toISOString(),
    operational_failure: String(error),
    stderr_tail: stderr.slice(-2000).replace(/sk-or-[A-Za-z0-9_-]+/g, "[redacted]"),
  };
} finally {
  child.kill();
}
writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n", { flag: "wx" });
const text = receipt.result?.content?.map((part) => part.text).join("\n") ?? JSON.stringify(receipt.operational_failure ?? receipt.rpc_error);
console.log(text);
process.exit(receipt.operational_failure || receipt.is_error || receipt.rpc_error ? 1 : 0);
