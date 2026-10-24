#!/usr/bin/env python3
"""Simulacion de economia (mochila vs tiempo). Uso: python3 tools/sim_mochila.py"""
from pathlib import Path
from lupa import LuaRuntime
root = Path(__file__).resolve().parent.parent
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(f'package.path = "{root.as_posix()}/src/?.lua;" .. package.path')
print(L.execute((root / "tools" / "sim_mochila.lua").read_text(encoding="utf-8")))
