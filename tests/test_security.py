#!/usr/bin/env python3
"""Security regressions with synthetic data; no root, desktop or real secrets."""
import ast
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "airootfs/usr/local/bin"
POLICY = BIN / "hyprarch-island-policy"
sanitize = runpy.run_path(str(BIN / "hyprarch-report-sanitize"))["sanitize"]


class SecurityTests(unittest.TestCase):
    def test_report_redaction(self):
        secrets = ["a.person@example.org", "2001:db8::1234", "::1",
                   "fe80::1234%eth0", "::ffff:192.0.2.5", "192.0.2.6",
                   "aa:bb:cc:dd:ee:ff", "ghp_abcdef123456", "sk-proj-abcdef123",
                   "/home/alice", "My home wifi"]
        text = "\n".join(secrets) + "\nAuthorization: Bearer supersecret\nSSID: My home wifi"
        clean = sanitize(text, ["My home wifi"])
        for secret in secrets + ["supersecret"]:
            self.assertNotIn(secret, clean)
        self.assertIn("/home/<usuario>", clean)
        self.assertEqual(sanitize("kernel 6.12; mesa 25.0; volume 40%"),
                         "kernel 6.12; mesa 25.0; volume 40%")
        self.assertEqual(sanitize("IPv6 [2001:db8::7], ::1."), "IPv6 [<ip>], <ip>.")

    def test_zip_and_web_use_same_sanitized_text(self):
        script = (BIN / "hyprarch-report").read_text(encoding="utf-8")
        blocks = [block.split("\nPY\n", 1)[0] for block in script.split("<<'PY'\n")[1:]]
        zipper = next(block for block in blocks if "zipfile.ZipFile" in block)
        payload = next(block for block in blocks if "privacy_version" in block)
        payload = payload.replace('"/usr/local/bin/hyprarch-report-sanitize"',
                                  repr(str(BIN / "hyprarch-report-sanitize")))
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            content = work / "content"
            content.mkdir()
            report = sanitize("kernel 6.12\na@example.org\n2001:db8::7\nBearer secret123\nSSID: My network\n")
            description = sanitize("/home/alice/project sk-proj-abc123")
            (content / "reporte.txt").write_text(report, encoding="utf-8", newline="\n")
            (content / "description.txt").write_text(description, encoding="utf-8", newline="\n")
            archive = work / "report.zip"
            out = work / "payload.json"
            env = dict(os.environ, HOME=str(work), USERPROFILE=str(work))
            try:
                subprocess.run([sys.executable, "-c", zipper, str(content), str(archive)], check=True, env=env)
                subprocess.run([sys.executable, "-c", payload, str(content), str(out), description], check=True, env=env)
                with zipfile.ZipFile(archive) as zipped:
                    archived = zipped.read("reporte.txt").decode("utf-8")
                sent = json.loads(out.read_text(encoding="utf-8"))
                self.assertEqual(archived, sent["report"])
                self.assertEqual(sent["description"], description)
                self.assertEqual(sent["privacy_version"], 1)
                self.assertNotIn("secret123", archived)
            finally:
                archive.unlink(missing_ok=True)

    def policy(self, work, event, grants=()):
        denied = work / "denials.jsonl"
        env = dict(os.environ, HYPRARCH_ISLAND_WORK=str(work),
                   HYPRARCH_ISLAND_GRANTS=json.dumps(list(grants)),
                   HYPRARCH_ISLAND_DENIALS=str(denied))
        result = subprocess.run([sys.executable, str(POLICY)], input=json.dumps(event),
                                text=True, capture_output=True, env=env, check=True)
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_island_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            work.mkdir()
            internal = {"tool_name": "Read", "tool_input": {"file_path": str(work / "notes.md")}}
            external = {"tool_name": "Read", "tool_input": {"file_path": str(work.parent / "secret.env")}}
            self.assertEqual(self.policy(work, internal), "allow")
            self.assertEqual(self.policy(work, external), "deny")
            self.assertEqual(self.policy(work, external, [external]), "allow")
            # Approval is scoped to this invocation and these exact arguments.
            self.assertEqual(self.policy(work, external), "deny")
            for command in ("cat ../secret.env", "ls ~", "/usr/local/bin/hyprarch-api system; cat ~/.ssh/id_ed25519",
                            "/usr/local/bin/hyprarch-api system $(id)", "python3 -c 'print(1)'"):
                event = {"tool_name": "Bash", "tool_input": {"command": command}}
                self.assertEqual(self.policy(work, event), "deny")
            event = {"tool_name": "Bash", "tool_input": {"command": "/usr/local/bin/hyprarch-api system"}}
            self.assertEqual(self.policy(work, event), "allow")
            event = {"tool_name": "Bash", "tool_input": {"command": "cat ../notes.txt"}}
            self.assertEqual(self.policy(work, event, [event]), "allow")
            self.assertEqual(self.policy(work, {"tool_name": "Edit", "tool_input": {}}), "deny")
            self.assertEqual(self.policy(work, {"tool_name": "mcp__other__exec", "tool_input": {}}), "deny")

    def test_policy_malformed_fails_closed(self):
        result = subprocess.run([sys.executable, str(POLICY)], input="{}", text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)

    @unittest.skipUnless(os.name == "posix", "symlink creation requires privilege on Windows; validate on Linux")
    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            work.mkdir()
            (work / "link").symlink_to(work.parent / "secret.env")
            event = {"tool_name": "Read", "tool_input": {"file_path": str(work / "link")}}
            self.assertEqual(self.policy(work, event), "deny")

    def test_embedded_python_syntax(self):
        # Parse actual heredocs, including the key importer and smoke controller.
        count = 0
        for path in (BIN / "hyprarch-install", BIN / "hyprarch-report"):
            text = path.read_text(encoding="utf-8")
            for block in text.split("<<'PY'\n")[1:]:
                ast.parse(block.split("\nPY\n", 1)[0], filename=str(path))
                count += 1
        self.assertGreaterEqual(count, 4)

    def test_ssh_snapshot_and_validation(self):
        keygen = shutil.which("ssh-keygen")
        if not keygen:
            self.skipTest("ssh-keygen not available")
        script = (BIN / "hyprarch-install").read_text(encoding="utf-8")
        importer = script.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        # O_NONBLOCK is meaningful for Linux special files. On Windows, emulate
        # its absence while testing the same importer on regular fixture files.
        runner = "import os,sys; os.O_NONBLOCK=getattr(os,'O_NONBLOCK',0); exec(sys.argv[3])"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for kind in ("ed25519", "ecdsa", "rsa"):
                key = root / kind
                command = [keygen, "-q", "-t", kind, "-N", "", "-f", str(key)]
                if kind == "rsa":
                    command += ["-b", "2048"]
                subprocess.run(command, check=True, capture_output=True, timeout=20)
                source = root / "supplied.pub"
                source.write_bytes(key.with_suffix(".pub").read_bytes())
                snapshot = root / (kind + ".snapshot")
                subprocess.run([sys.executable, "-c", runner, str(source), str(snapshot), importer], check=True)
                before = snapshot.read_bytes()
                # Replacing the original after import must not alter the key used.
                source.write_text("now a different file", encoding="utf-8")
                self.assertEqual(snapshot.read_bytes(), before)
                subprocess.run([keygen, "-l", "-f", str(snapshot)], check=True, capture_output=True)
            for index, invalid in enumerate((key.read_bytes(), before + before, b"command=evil " + before,
                                             b"ssh-dss AAAA\n", b"ssh-ed25519 not-base64!\n")):
                source.write_bytes(invalid)
                snapshot = root / ("invalid" + str(index))
                result = subprocess.run([sys.executable, "-c", runner, str(source), str(snapshot), importer])
                self.assertEqual(result.returncode, 1)
                self.assertFalse(snapshot.exists())


if __name__ == "__main__":
    unittest.main()
