"""Bounded stdlib JSON-RPC transport for synthetic MCP checks, without model calls."""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time


class Rpc:
    def __init__(self, command: list[str], log: Path, *, env=None, cwd=None, mcp=True, timeout=120):
        self.log = log.open('w')
        self.proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=self.log, text=True,
                                     bufsize=1, start_new_session=True)
        self.messages = queue.Queue()
        self.counter = 0
        self.timeout = timeout
        self.mcp = mcp
        self.events = []
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()

    def read(self):
        try:
            while True:
                line = self.proc.stdout.readline(8 * 1024 * 1024)
                if not line:
                    raise RuntimeError('RPC process closed stdout')
                if len(line) >= 8 * 1024 * 1024:
                    raise RuntimeError('RPC response exceeds observation limit')
                self.messages.put(json.loads(line))
        except Exception as error:
            self.messages.put(error)

    def send(self, message):
        if self.mcp:
            message = dict(message, jsonrpc='2.0')
        self.proc.stdin.write(json.dumps(message) + '\n')
        self.proc.stdin.flush()

    def call(self, method, params):
        return self.exchange({'method': method, 'params': params})

    def exchange(self, request):
        self.counter += 1
        ident = self.counter
        self.events = []
        self.send(dict(request, id=ident))
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                message = self.messages.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                raise RuntimeError('RPC deadline exceeded') from None
            if isinstance(message, Exception):
                raise RuntimeError('Invalid RPC stream: ' + type(message).__name__) from None
            if message.get('id') == ident:
                if 'error' in message:
                    raise RuntimeError('RPC request rejected')
                return message.get('result', message)
            self.events.append(message)
            if 'id' in message and 'method' in message:
                self.send({'id': message['id'], 'error': {'code': -32601, 'message': 'Unsupported client request'}})

    def initialize(self):
        result = self.call('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                                         'clientInfo': {'name': 're-doctor', 'version': '1.0.0'}})
        self.send({'method': 'notifications/initialized'})
        return result

    def tool(self, name, arguments):
        result = self.call('tools/call', {'name': name, 'arguments': arguments})
        text = '\n'.join(c.get('text', '') for c in result.get('content', []) if c.get('type') == 'text')
        return result, text

    def close(self):
        if self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGTERM)
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(self.proc.pid, signal.SIGKILL)
            self.proc.wait(timeout=10)
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
