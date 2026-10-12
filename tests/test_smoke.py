#!/usr/bin/env python3
"""Exercise the actual smoke PPM/serial analyzers without QEMU."""
import ast
import collections
import os
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "tools/smoke_boot.sh").read_text(encoding="utf-8")
source = text.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
tree = ast.parse(source)
# Load only the pure analyzers; do not execute run() or launch a VM.
definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
               and node.name in {"pixels_ok", "serial_log"}]
scope = dict(collections=collections, re=re, black_max=0.99, dominant_max=0.995)
exec(compile(ast.Module(body=definitions, type_ignores=[]), "smoke_boot.sh", "exec"), scope)


class SmokeTests(unittest.TestCase):
    def test_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            ppm = Path(directory) / "frame.ppm"
            for data, expected in ((b"\0\0\0" * 100, False), (b"\xff\xff\xff" * 100, False),
                                   (b"\xff\0\0\0\xff\0" * 50, True)):
                ppm.write_bytes(b"P6\n10 10\n255\n" + data)
                self.assertEqual(scope["pixels_ok"](ppm), expected)
            for data in (b"P6\n10 10\n255\n\x00", b"P3\n10 10\n255\n"):
                ppm.write_bytes(data)
                with self.assertRaises(ValueError):
                    scope["pixels_ok"](ppm)

    def test_serial(self):
        with tempfile.TemporaryDirectory() as directory:
            scope["out"] = Path(directory)
            serial = Path(directory) / "serial.log"
            self.assertEqual(scope["serial_log"](), b"")
            serial.write_bytes(b"HYPRARCH_DESKTOP_READY\n")
            self.assertIn(b"HYPRARCH_DESKTOP_READY", scope["serial_log"]())
            serial.write_bytes(b"Kernel panic - not syncing")
            with self.assertRaises(RuntimeError):
                scope["serial_log"]()


if __name__ == "__main__":
    unittest.main()
