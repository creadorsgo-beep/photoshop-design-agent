#!/usr/bin/env python3
"""
One-shot runner: uses pre-analyzed data to skip the Claude API call
and go straight to Photoshop generation using the design template.
"""
import os, sys, re, subprocess, time, socket
from datetime import datetime
from pathlib import Path

PROJECT_DIR   = Path(__file__).parent.parent
MCP_DIR       = Path("C:/Users/Estudio Creador/Desktop/mpc photoshop/mcp")
PROXY_DIR     = Path("C:/Users/Estudio Creador/Desktop/mpc photoshop/adb-proxy-socket")
NODE_EXE      = "C:/Program Files/Adobe/Adobe Photoshop 2026/node.exe"
OUTPUT_DIR    = PROJECT_DIR / "output"
TEMPLATE_PATH = "C:/Users/Estudio Creador/Documents/plantilla youtube.psd"

sys.path.insert(0, str(MCP_DIR))
sys.path.insert(0, str(PROJECT_DIR / "tools"))

from dotenv import load_dotenv
load_dotenv(PROJECT_DIR / ".env")

# ── Pre-analyzed data (from Claude Code session) ───────────────────────────────
DATA = {
    "bible_ref"   : "Salmo 63:1-2",
    "title_l1"    : "ORACION",
    "title_l2"    : "DE DAVID",
    "image_prompt": (
        "A lone man in ancient robes kneeling in prayer in the rocky Judean desert "
        "at dawn. Parched earth, dramatic golden sunrise light across arid hills. "
        "Cinematic documentary photography, National Geographic style. No text."
    ),
}
VIDEO_TITLE = "ORACION DE DAVID - Salmo 63"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def ensure_proxy():
    try:
        with socket.create_connection(("localhost", 3001), timeout=2):
            log("Proxy already running on :3001")
            return
    except (ConnectionRefusedError, OSError):
        pass
    log("Starting MCP proxy...")
    subprocess.Popen([NODE_EXE, "proxy.js"], cwd=str(PROXY_DIR),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    log("Proxy started.")


def ps_init():
    import socket_client
    from core import init, sendCommand, createCommand
    socket_client.configure(app="photoshop", url="http://localhost:3001", timeout=90)
    init("photoshop", socket_client)
    global _send_cmd, _create_cmd
    _send_cmd   = sendCommand
    _create_cmd = createCommand

def _ps(cmd, params):
    return _send_cmd(_create_cmd(cmd, params))


def ps_update_texts(title_l1, title_l2, bible_ref):
    """Update the template's named text layers via JSX."""
    from ps_executor import _eval

    def esc(s):
        return s.replace("\\", "\\\\").replace("'", "\\'")

    jsx = f"""
var doc = app.activeDocument;
for (var i = 0; i < doc.layers.length; i++) {{
    var l = doc.layers[i];
    if (l.kind === LayerKind.TEXT) {{
        if (l.name === 'Titulo L1')  l.textItem.contents = '{esc(title_l1)}';
        if (l.name === 'Titulo L2')  l.textItem.contents = '{esc(title_l2)}';
        if (l.name === 'Referencia') l.textItem.contents = '{esc(bible_ref)}';
    }}
}}
'done';
"""
    return _eval(jsx)


def main():
    log("=" * 52)
    log(f"Post Generator (pre-analyzed) — {datetime.now().strftime('%Y-%m-%d')}")
    log("=" * 52)
    log(f"Title L1   : {DATA['title_l1']}")
    log(f"Title L2   : {DATA['title_l2']}")
    log(f"Bible ref  : {DATA['bible_ref']}")
    log(f"Img prompt : {DATA['image_prompt'][:70]}...")

    ensure_proxy()
    ps_init()

    # Open template
    log("Opening template...")
    from ps_executor import open_template, export_as_jpg, _eval
    open_template(TEMPLATE_PATH)

    # Rename existing "Fondo IA" so Firefly creates a fresh layer on top
    _eval("""
var doc = app.activeDocument;
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name === 'Fondo IA') { doc.layers[i].name = 'Fondo IA OLD'; break; }
}
'done';
""")

    # Generate AI image — Firefly places it at top of stack
    log("Generating AI image with Adobe Firefly (~30s)...")
    _ps("generateImage", {
        "layerName": "Fondo IA",
        "prompt": DATA["image_prompt"],
        "contentType": "photo"
    })

    # Move new "Fondo IA" above "Fondo" (background) and delete old one
    _eval("""
var doc = app.activeDocument;
var newLayer = null, oldLayer = null, fondoLayer = null;
for (var i = 0; i < doc.layers.length; i++) {
    var l = doc.layers[i];
    if (l.name === 'Fondo IA' && !newLayer) newLayer = l;
    if (l.name === 'Fondo IA OLD') oldLayer = l;
    if (l.name === 'Fondo') fondoLayer = l;
}
if (newLayer && fondoLayer) newLayer.move(fondoLayer, ElementPlacement.PLACEBEFORE);
if (oldLayer) oldLayer.remove();
'done';
""")

    # Update text layers
    log("Updating text layers...")
    ps_update_texts(DATA["title_l1"], DATA["title_l2"], DATA["bible_ref"])

    # Export
    safe_title = re.sub(r"[^\w]", "_", VIDEO_TITLE)[:40].lower()
    date_str   = datetime.now().strftime("%Y%m%d")
    out_path   = str(OUTPUT_DIR / f"{date_str}_{safe_title}.jpg")
    log(f"Saving to {out_path}...")
    export_as_jpg(out_path, quality=85)

    log(f"Done! Post saved: {out_path}")
    return out_path


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
