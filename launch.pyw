# -*- coding: utf-8 -*-
"""Launcher script - double-click this file to start the app.
Uses current Python interpreter, so PATH must include pythonw.exe
or this .pyw must be associated with a Python installation."""
import os
import sys
import subprocess
import traceback

app_dir = os.path.dirname(os.path.abspath(__file__))
app_py = os.path.join(app_dir, "app.py")

try:
    subprocess.Popen([sys.executable, app_py], cwd=app_dir)
except Exception:
    err = traceback.format_exc()
    with open(os.path.join(app_dir, "launch_err.log"), "a", encoding="utf-8") as f:
        f.write(f"[launch.pyw] {err}\n")
