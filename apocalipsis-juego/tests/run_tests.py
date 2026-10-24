#!/usr/bin/env python3
"""Pruebas de Lua puro con lupa (pip install lupa). Uso: python3 apocalipsis-juego/tests/run_tests.py"""
import sys
from pathlib import Path
from lupa import LuaRuntime
root = Path(__file__).resolve().parent.parent
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(f'package.path = "{root.as_posix()}/src/?.lua;" .. package.path')
failed = L.execute((root / "tests" / "run.lua").read_text(encoding="utf-8"))
sys.exit(1 if failed else 0)
