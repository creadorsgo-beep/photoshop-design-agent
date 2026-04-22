#!/usr/bin/env python3
"""Entry point for the Design Agent GUI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from gui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
