#!/usr/bin/env node
// Call real Jev MCP tools (@jkudish/jev-mcp over stdio) and keep an immutable receipt per call.
//
//   node tools/jev_call.mjs --run RUN_DIR --id DECISION_ID --tool jev_decide --args args.json [--purpose "..."] [--evidence-file path ...]
//
// RUN_DIR is created if missing; each call writes RUN_DIR/<id>.json holding the exact request, the full
// MCP result, SHA-256 of every named evidence file, wall time, and server/model identity. An existing
// receipt is never overwritten. API keys are read from the environment, redacted from anything the
// recorder stores, and never written. Arguments are validated before any file is created; a failing
// server or a malformed reply still produces a receipt that says what went wrong.
//
// Test hooks: --server runs a JS file with node instead of the package; --command replaces npx.
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

const PACKAGE = `@jkudish/jev-mcp@${process.env.JEV_MCP_VERSION ?? "0.14.1"}`;

function usage(message) {
  console.error(message);
  process.exit(2);
}

let values;
try {
  ({ values } = parseArgs({
    options: {
      run: { type: "string" },
      id: { type: "string" },
      tool: { type: "string" },
      args: { type: "string" },
      purpose: { type: "string", default: "" },
      "evidence-file": { type: "string", multiple: true, default: [] },
      server: { type: "string", default: process.env.JEV_MCP_BIN ?? "" },
      command: { type: "string", default: "" },
      timeout: { type: "string", default: "180000" },
    },
  }));
} catch (error) {
  usage(String(error.message ?? error));
}
for (const key of ["run", "id", "tool", "args"]) {
  if (!values[key]) usage(`missing --${key}`);
}
if (!/^[A-Za-z0-9._-]+$/.test(values.id)) usage("--id must be a stable slug");
const timeoutMs = Number(values.timeout);
if (!Number.isFinite(timeoutMs) || timeoutMs <= 0 || timeoutMs > 2 ** 31 - 1) usage("--timeout must be between 1 and 2147483647 milliseconds");

const sha256 = (buffer) => createHash("sha256").update(buffer).digest("hex");
function readOrExit(path, what) {
  try {
    return readFileSync(path);
  } catch (error) {
    return usage(`cannot read ${what} ${path}: ${error.code ?? error.message}`);
  }
}
const argsBytes = readOrExit(values.args, "--args");
let toolArgs;
try {
  toolArgs = JSON.parse(argsBytes.toString("utf8"));
} catch (error) {
  usage(`--args is not valid JSON: ${error.message}`);
}
const evidenceFiles = values["evidence-file"].map((path) => {
  const bytes = readOrExit(path, "--evidence-file");
  return { path, sha256: sha256(bytes), bytes: bytes.length };
});

const runDir = resolve(values.run);
const receiptPath = join(runDir, `${values.id}.json`);
if (existsSync(receiptPath)) usage(`receipt exists, not overwriting: ${receiptPath}`);
mkdirSync(runDir, { recursive: true });

// Literal key values are redacted wherever recorder-controlled text is stored.
const secrets = ["OPENROUTER_API_KEY", "TYPESAFE_API_KEY"].map((name) => process.env[name]).filter((value) => value && value.length >= 8);
const redact = (text) => secrets.reduce((out, secret) => out.split(secret).join("[redacted]"), String(text)).replace(/sk-or-[A-Za-z0-9_-]+/g, "[redacted]");

const command = values.command || (values.server ? process.execPath : "npx");
const serverArgs = values.server ? [values.server] : ["-y", PACKAGE];
const env = { ...process.env, JEV_MCP_MODEL: process.env.JEV_MCP_MODEL ?? "typesafe/jev-1.13" };

const nonJsonLines = [];
const pending = new Map();
let stderr = "";
let buffer = "";
let nextId = 1;
let childFailure = null;

function failPending(reason) {
  childFailure ??= reason;
  for (const [id, entry] of pending) {
    clearTimeout(entry.timer);
    entry.reject(new Error(reason));
    pending.delete(id);
  }
}

const child = spawn(command, serverArgs, { env, stdio: ["pipe", "pipe", "pipe"] });
child.on("error", (error) => failPending(`could not run the server (${command}): ${error.code ?? error.message}`));
// "close" fires after the stdio streams have ended, so a reply written just before exit is already handled.
child.on("close", (code, signal) => failPending(`server exited before replying (code ${code}, signal ${signal})`));
child.stdin.on("error", () => {}); // a dead server is reported through the exit/error handlers
child.stderr.setEncoding("utf8");
child.stderr.on("data", (chunk) => (stderr += chunk));
child.stdout.setEncoding("utf8"); // decode once so multibyte characters split across chunks stay intact
child.stdout.on("data", (chunk) => {
  buffer += chunk;
  let newline;
  while ((newline = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, newline).trim();
    buffer = buffer.slice(newline + 1);
    if (!line) continue;
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      nonJsonLines.push(redact(line).slice(0, 200));
      continue;
    }
    if (message.id !== undefined && pending.has(message.id)) {
      const entry = pending.get(message.id);
      clearTimeout(entry.timer);
      pending.delete(message.id);
      entry.resolve(message);
    }
  }
});

const rpc = (method, params) =>
  new Promise((resolvePromise, reject) => {
    if (childFailure) return reject(new Error(childFailure));
    const id = nextId++;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`timeout on ${method}`));
    }, timeoutMs);
    pending.set(id, { resolve: resolvePromise, reject, timer });
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  });

const started = Date.now();
const base = {
  id: values.id,
  purpose: values.purpose,
  tool: values.tool,
  server_package: values.server ? `local:${values.server}` : PACKAGE,
  arguments: toolArgs,
  args_file: values.args,
  args_sha256: sha256(argsBytes),
  evidence_files: evidenceFiles,
  started_utc: new Date(started).toISOString(),
};
let receipt;
try {
  const init = await rpc("initialize", { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "fr2-jev-ledger", version: "1" } });
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  const call = await rpc("tools/call", { name: values.tool, arguments: toolArgs });
  receipt = {
    ...base,
    server: init.result?.serverInfo ?? null,
    model: env.JEV_MCP_MODEL,
    provider_env: env.TYPESAFE_API_KEY ? "typesafe" : env.OPENROUTER_API_KEY ? "openrouter" : "none",
    seconds: (Date.now() - started) / 1000,
    rpc_error: call.error ?? null,
    is_error: call.result?.isError ?? false,
    non_json_stdout_lines: nonJsonLines,
    result: call.result ?? null,
  };
} catch (error) {
  receipt = {
    ...base,
    seconds: (Date.now() - started) / 1000,
    operational_failure: redact(error.message ?? error),
    non_json_stdout_lines: nonJsonLines,
    stderr_tail: redact(stderr.slice(-2000)),
  };
} finally {
  child.kill();
}
writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n", { flag: "wx" });
const text = receipt.result?.content?.map((part) => part.text).join("\n") ?? JSON.stringify(receipt.operational_failure ?? receipt.rpc_error);
console.log(text);
process.exit(receipt.operational_failure || receipt.is_error || receipt.rpc_error ? 1 : 0);
