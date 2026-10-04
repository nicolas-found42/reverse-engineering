// node --test tools/jev_call.test.mjs
// Runs the receipt recorder against a fake MCP server; no network and no real key are used.
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const recorder = join(here, "jev_call.mjs");

function workspace(fakeBody) {
  const dir = mkdtempSync(join(tmpdir(), "jevcall-"));
  const server = join(dir, "fake-server.mjs");
  writeFileSync(
    server,
    `import { createInterface } from "node:readline";
const rl = createInterface({ input: process.stdin });
rl.on("line", (line) => {
  const message = JSON.parse(line);
  if (message.method === "initialize") reply(message.id, { serverInfo: { name: "fake", version: "9.9.9" } });
  if (message.method === "tools/call") { ${fakeBody} }
});
function reply(id, result) { process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + "\\n"); }
`,
  );
  const args = join(dir, "args.json");
  writeFileSync(args, JSON.stringify({ text: "x" }));
  return { dir, server, args, run: join(dir, "run") };
}

function record(ws, extra = [], env = {}) {
  return spawnSync(
    process.execPath,
    [recorder, "--run", ws.run, "--id", "r1", "--tool", "jev_screen", "--args", ws.args, "--server", ws.server, ...extra],
    { env: { ...process.env, ...env }, encoding: "utf8" },
  );
}
const receipt = (ws) => JSON.parse(readFileSync(join(ws.run, "r1.json"), "utf8"));

test("multibyte text split across stdout chunks is preserved exactly", () => {
  const ws = workspace(`reply(message.id, { content: [{ type: "text", text: "€😀".repeat(40000) }] });`);
  const done = record(ws);
  assert.equal(done.status, 0, done.stderr);
  assert.equal(receipt(ws).result.content[0].text, "€😀".repeat(40000));
});

test("a non-JSON stdout line does not lose the receipt and is recorded", () => {
  const ws = workspace(`process.stdout.write("warning: not json\\n"); reply(message.id, { content: [{ type: "text", text: "ok" }] });`);
  const done = record(ws);
  assert.equal(done.status, 0, done.stderr);
  const r = receipt(ws);
  assert.equal(r.result.content[0].text, "ok");
  assert.deepEqual(r.non_json_stdout_lines, ["warning: not json"]);
});

test("a missing server command is recorded as an operational failure, not a stack trace", () => {
  const ws = workspace(`reply(message.id, {});`);
  const done = record(ws, ["--command", join(ws.dir, "no-such-binary")]);
  assert.equal(done.status, 1);
  assert.doesNotMatch(done.stderr, /at .*node:internal/);
  assert.match(receipt(ws).operational_failure, /ENOENT|no-such-binary|spawn/);
});

test("key values are redacted from the recorded stderr tail", () => {
  const key = "sk-test-SECRET-0123456789";
  const ws = workspace(`process.stderr.write("auth failed for ${key}\\n"); process.exit(3);`);
  const done = record(ws, [], { OPENROUTER_API_KEY: key, TYPESAFE_API_KEY: "tsk_plain_value_98765" });
  assert.equal(done.status, 1);
  const text = readFileSync(join(ws.run, "r1.json"), "utf8");
  assert.doesNotMatch(text, /SECRET-0123456789/);
  assert.match(text, /\[redacted\]/);
});

test("bad arguments exit 2 before any file is created", () => {
  const ws = workspace(`reply(message.id, {});`);
  for (const extra of [["--timeout", "abc"], ["--evidence-file", join(ws.dir, "missing.txt")]]) {
    const done = record(ws, extra);
    assert.equal(done.status, 2, `${extra}: ${done.stderr}`);
    assert.doesNotMatch(done.stderr, /at .*node:internal/);
    assert.equal(existsSync(ws.run), false, `${extra} created the run directory`);
  }
});

test("an existing receipt is never overwritten", () => {
  const ws = workspace(`reply(message.id, { content: [{ type: "text", text: "first" }] });`);
  assert.equal(record(ws).status, 0);
  const before = readFileSync(join(ws.run, "r1.json"), "utf8");
  const again = record(ws);
  assert.equal(again.status, 2);
  assert.equal(readFileSync(join(ws.run, "r1.json"), "utf8"), before);
});

test("a server that flushes its reply and then exits still yields the reply", () => {
  const ws = workspace(`process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id: message.id, result: { content: [{ type: "text", text: "x".repeat(200000) }] } }) + "\\n", () => process.exit(0));`);
  for (let attempt = 0; attempt < 5; attempt++) {
    const dir = ws.run + attempt;
    const done = spawnSync(process.execPath, [recorder, "--run", dir, "--id", "r1", "--tool", "jev_screen", "--args", ws.args, "--server", ws.server], { encoding: "utf8" });
    assert.equal(done.status, 0, done.stderr);
    const r = JSON.parse(readFileSync(join(dir, "r1.json"), "utf8"));
    assert.equal(r.operational_failure, undefined);
    assert.equal(r.result.content[0].text.length, 200000);
  }
});

test("an oversized timeout is rejected instead of firing immediately", () => {
  const ws = workspace(`reply(message.id, {});`);
  const done = record(ws, ["--timeout", "3000000000"]);
  assert.equal(done.status, 2, done.stderr);
  assert.equal(existsSync(ws.run), false);
});

test("a key split by the 200-character cut is still redacted", () => {
  const key = "sk-test-SECRET-0123456789";
  const ws = workspace(`process.stdout.write("a".repeat(180) + "${key}" + "\\n"); reply(message.id, { content: [{ type: "text", text: "ok" }] });`);
  const done = record(ws, [], { OPENROUTER_API_KEY: key });
  assert.equal(done.status, 0, done.stderr);
  const text = readFileSync(join(ws.run, "r1.json"), "utf8");
  assert.doesNotMatch(text, /SECRE/);
});
