#!/usr/bin/env python3
"""Portable stdio integration tests: python tests/test_mcp.py [server]."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import time
import threading

READ_ONLY = {
    "hyprarch_windows", "hyprarch_workspaces", "hyprarch_active",
    "hyprarch_apps", "hyprarch_mode_get", "hyprarch_volume_get",
    "hyprarch_system",
}
ALL_TOOLS = READ_ONLY | {
    "hyprarch_focus", "hyprarch_close", "hyprarch_open", "hyprarch_mode_set",
    "hyprarch_theme_set", "hyprarch_volume_set", "hyprarch_brightness_set",
    "hyprarch_screenshot", "hyprarch_notify",
}
FAKE = """#!/usr/bin/env python3
import json
import sys
import time
if sys.argv[1:] == ["system"]:
    time.sleep(30)
elif sys.argv[1:] != ["windows"]:
    if sys.argv[1:] == ["screenshot"]:
        print(json.dumps({"ok": True, "path": "/private/capture.png"}))
        sys.exit(0)
    sys.exit(64)
print(json.dumps({"ok": True, "fake": True}))
"""


def check_session(server, fake, readonly=False):
    env = dict(
        os.environ,
        HYPRARCH_API_BIN=str(fake),
        HYPRARCH_API_PYTHON=sys.executable,
        HYPRARCH_MCP_READONLY="1" if readonly else "0",
    )
    version = "2024-11-05" if readonly else "2025-06-18"
    p = subprocess.Popen(
        [sys.executable, "-B", str(server)],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    sequence = 0
    replies = queue.Queue()

    def read_replies():
        for line in p.stdout:
            replies.put(line)
        replies.put(None)

    reader = threading.Thread(target=read_replies, daemon=True)
    reader.start()

    def send(message):
        p.stdin.write(json.dumps(message) + "\n")
        p.stdin.flush()

    def rpc(method, params=None):
        nonlocal sequence
        sequence += 1
        send({
            "jsonrpc": "2.0",
            "id": sequence,
            "method": method,
            "params": {} if params is None else params,
        })
        try:
            line = replies.get(timeout=30)
        except queue.Empty as error:
            raise AssertionError("El servidor no respondio en 30 segundos") from error
        assert line, "El servidor termino prematuramente"
        response = json.loads(line)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == sequence
        assert ("result" in response) != ("error" in response)
        return response

    def call(name, arguments=None):
        return rpc("tools/call", {
            "name": name,
            "arguments": {} if arguments is None else arguments,
        })

    try:
        initialized = rpc("initialize", {
            "protocolVersion": version,
            "capabilities": {},
            "clientInfo": {"name": "test_mcp", "version": "1"},
        })["result"]
        assert initialized == {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hyprarch-mcp", "version": "0.1.0"},
        }

        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        assert rpc("ping")["result"] == {}

        tools = rpc("tools/list")["result"]["tools"]
        assert {tool["name"] for tool in tools} == (
            READ_ONLY if readonly else ALL_TOOLS
        )
        assert all(
            t["inputSchema"]["additionalProperties"] is False for t in tools
        )

        result = call("hyprarch_windows")["result"]
        assert result["isError"] is False
        assert json.loads(result["content"][0]["text"]) == {
            "ok": True, "fake": True,
        }
        assert rpc("inexistente")["error"]["code"] == -32601

        if readonly:
            response = call("hyprarch_open", {"app": "Firefox"})
            assert response["error"]["code"] == -32602
        else:
            result = call("hyprarch_screenshot")["result"]
            assert result["isError"] is False
            assert json.loads(result["content"][0]["text"])["path"] == "/private/capture.png"
            response = call("hyprarch_open", {"app": "Firefox\n"})
            assert response["error"]["code"] == -32602
            response = call("hyprarch_volume_set", {"percent": True})
            assert response["error"]["code"] == -32602

            started = time.monotonic()
            result = call("hyprarch_system")["result"]
            assert result["isError"] is True
            assert "Timeout" in result["content"][0]["text"]
            assert time.monotonic() - started >= 19
            assert rpc("ping")["result"] == {}

        p.stdin.close()
        assert p.wait(timeout=5) == 0
        reader.join(timeout=5)
        assert replies.get(timeout=5) is None, "Salida adicional inesperada"
        assert p.stderr.read().strip(), "Falta el registro de llamadas"
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        for stream in (p.stdin, p.stdout, p.stderr):
            stream.close()


def main():
    server = Path(
        sys.argv[1] if len(sys.argv) > 1 else
        Path(__file__).resolve().parents[1] / "airootfs/usr/local/bin/hyprarch-mcp"
    ).resolve()

    with tempfile.TemporaryDirectory(prefix="hyprarch-mcp-test-") as directory:
        fake = Path(directory) / "hyprarch-api"
        fake.write_text(FAKE, encoding="utf-8")
        fake.chmod(0o700)
        check_session(server, fake)
        check_session(server, fake, readonly=True)

    print("OK: initialize, tools/list, llamada, validacion, timeout y solo lectura")


if __name__ == "__main__":
    main()
