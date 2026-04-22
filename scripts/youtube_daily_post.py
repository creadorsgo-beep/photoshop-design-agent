#!/usr/bin/env python3
"""
youtube_daily_post.py
Generates an Instagram post from the latest video of a YouTube channel.
Designed to run daily at 23:00 via Windows Task Scheduler.
"""

import os
import sys
import re
import json
import subprocess
import time
import socket
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent.parent
MCP_DIR     = Path("C:/Users/Estudio Creador/Desktop/mpc photoshop/mcp")
PROXY_DIR   = Path("C:/Users/Estudio Creador/Desktop/mpc photoshop/adb-proxy-socket")
NODE_EXE    = "C:/Program Files/Adobe/Adobe Photoshop 2026/node.exe"
OUTPUT_DIR  = PROJECT_DIR / "output"
LOGS_DIR    = PROJECT_DIR / "logs"

CHANNEL_URL  = "https://www.youtube.com/@100biblialuisvalladare2/videos"
CHANNEL_NAME = "100% Biblia - Luis Valladares"
FONT_BOLD    = "HelveticaNeueLTStd-BdEx"

OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(MCP_DIR))
sys.path.insert(0, str(PROJECT_DIR / "tools"))

from dotenv import load_dotenv
load_dotenv(PROJECT_DIR / ".env")

# ── Proxy ─────────────────────────────────────────────────────────────────────
def ensure_proxy():
    try:
        with socket.create_connection(("localhost", 3001), timeout=2):
            log("Proxy already running on :3001")
            return
    except (ConnectionRefusedError, OSError):
        pass
    log("Starting MCP proxy...")
    subprocess.Popen(
        [NODE_EXE, "proxy.js"],
        cwd=str(PROXY_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)
    log("Proxy started.")


# ── Photoshop via socket ───────────────────────────────────────────────────────
def ps_init():
    import socket_client
    from core import init, sendCommand, createCommand

    socket_client.configure(app="photoshop", url="http://localhost:3001", timeout=90)
    init("photoshop", socket_client)

    # Store references globally for helper functions
    global _send_cmd, _create_cmd
    _send_cmd   = sendCommand
    _create_cmd = createCommand

def _ps(cmd_name, params):
    return _send_cmd(_create_cmd(cmd_name, params))

def ps_create_document(name, w=1080, h=1080, res=72):
    return _ps("createDocument", {
        "documentName": name, "width": w, "height": h,
        "resolution": res, "fillColor": {"red": 0, "green": 0, "blue": 0},
        "colorMode": "RGB"
    })

def ps_generate_image(layer_name, prompt, content_type="photo"):
    return _ps("generateImage", {
        "layerName": layer_name, "prompt": prompt, "contentType": content_type
    })

def ps_create_pixel_layer(name):
    return _ps("createPixelLayer", {"layerName": name, "fillNeutral": False, "opacity": 100})

def ps_select_rectangle(layer_id, bounds, feather=0):
    return _ps("selectRectangle", {
        "layerId": layer_id, "bounds": bounds, "feather": feather, "antiAlias": True
    })

def ps_fill_selection(layer_id, color, opacity=100):
    return _ps("fillSelection", {
        "layerId": layer_id, "color": color, "blendMode": "NORMAL", "opacity": opacity
    })

def ps_save_as(file_path, file_type="JPG"):
    return _ps("saveDocumentAs", {"filePath": file_path, "fileType": file_type})


def ps_add_texts(title_l1, title_l2, bible_ref):
    """Add all text layers centered via JSX (bypasses MCP bounds bug)."""
    from ps_executor import _eval

    def esc(s):
        return s.replace("'", "\\'").replace('"', '\\"')

    jsx = f"""
var doc = app.activeDocument;
function addCenteredText(txt, font, size, r, g, b, topPx, heightPx, opacity) {{
    var layer = doc.artLayers.add();
    layer.kind = LayerKind.TEXT;
    var ti = layer.textItem;
    ti.kind = TextType.PARAGRAPHTEXT;
    ti.contents = txt;
    ti.font = font;
    ti.size = new UnitValue(size, 'pt');
    ti.color.rgb.red = r;
    ti.color.rgb.green = g;
    ti.color.rgb.blue = b;
    ti.justification = Justification.CENTER;
    ti.position = [new UnitValue(54, 'px'), new UnitValue(topPx, 'px')];
    ti.width  = new UnitValue(972, 'px');
    ti.height = new UnitValue(heightPx, 'px');
    if (opacity !== 100) layer.opacity = opacity;
}}
addCenteredText('{esc(title_l1)}', '{FONT_BOLD}', 76, 255, 255, 255, 715, 105, 100);
addCenteredText('{esc(title_l2)}', '{FONT_BOLD}', 76, 255, 255, 255, 828, 105, 100);
addCenteredText('{esc(bible_ref)}', '{FONT_BOLD}', 28, 212, 175, 55,  940,  60, 100);
addCenteredText('{esc(CHANNEL_NAME)}', '{FONT_BOLD}', 20, 190, 190, 190, 1010, 50,  80);
'done';
"""
    return _eval(jsx)


# ── YouTube ───────────────────────────────────────────────────────────────────
def get_latest_video():
    result = subprocess.run(
        [sys.executable, "-m", "yt_dlp",
         "--flat-playlist", "--playlist-items", "1",
         "--print", "%(title)s|||%(id)s",
         CHANNEL_URL],
        capture_output=True, text=True, timeout=60
    )
    line = result.stdout.strip().split("\n")[0]
    title, video_id = line.split("|||", 1)
    return video_id.strip(), title.strip()


def get_transcript(video_id):
    vtt_path = OUTPUT_DIR / f"yt_{video_id}.es.vtt"
    if not vtt_path.exists():
        subprocess.run(
            [sys.executable, "-m", "yt_dlp",
             "--write-auto-sub", "--sub-lang", "es", "--skip-download",
             "--output", str(OUTPUT_DIR / f"yt_{video_id}.%(ext)s"),
             f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, timeout=120
        )
    if not vtt_path.exists():
        return ""
    content = vtt_path.read_text(encoding="utf-8", errors="ignore")
    lines, seen, out = content.split("\n"), set(), []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(("WEBVTT", "NOTE")) or "-->" in line or re.match(r"^\d+$", line):
            continue
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return " ".join(out)


# ── Claude API ────────────────────────────────────────────────────────────────
def analyze_video(title, transcript):
    """Uses Claude to extract Bible ref and build photorealistic Firefly prompt."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    system = """You are a social media designer for a Bible devotional channel.
Given a video title and transcript, return a JSON object with these keys:
- bible_ref   : main Bible reference as a string (e.g. "Mateo 2:3-5")
- title_l1    : first line of the title in UPPERCASE, max 13 chars, no accents for JSX safety
- title_l2    : second line of the title in UPPERCASE, max 15 chars, no accents
- image_prompt: a vivid photorealistic scene in English for Adobe Firefly (max 220 chars).
                Style: documentary photography, National Geographic, cinematic lighting.
                Must depict the biblical scene described in the video. NO text in image.
Return ONLY valid JSON."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system,
        messages=[{
            "role": "user",
            "content": f"Title: {title}\n\nTranscript:\n{transcript[:3000]}"
        }]
    )
    raw = msg.content[0].text.strip()
    # Strip markdown code blocks if present
    raw = re.sub(r"^```json\s*|^```\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


# ── Helpers ───────────────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)


def find_layer_id(layers, name):
    for l in layers:
        if l.get("name") == name:
            return l["id"]
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    log("=" * 52)
    log(f"YouTube Daily Post — {datetime.now().strftime('%Y-%m-%d')}")
    log("=" * 52)

    # 1. Proxy + Photoshop connection
    ensure_proxy()
    ps_init()

    # 2. Latest video
    log("Fetching latest video from channel...")
    video_id, title = get_latest_video()
    log(f"Video: {title}  (id={video_id})")

    # 3. Transcript
    log("Downloading subtitles...")
    transcript = get_transcript(video_id)
    log(f"Transcript: {len(transcript)} chars")

    # 4. Analyze with Claude
    log("Analyzing content with Claude...")
    data = analyze_video(title, transcript)
    log(f"  Title L1   : {data['title_l1']}")
    log(f"  Title L2   : {data['title_l2']}")
    log(f"  Bible ref  : {data['bible_ref']}")
    log(f"  Img prompt : {data['image_prompt'][:70]}...")

    # 5. Create Photoshop document
    log("Creating 1080x1080 Photoshop document...")
    ps_create_document(f"Post {datetime.now().strftime('%Y-%m-%d')}")

    # 6. Generate AI image (Firefly, photorealistic)
    log("Generating AI image with Adobe Firefly (may take ~30s)...")
    ps_generate_image("Fondo IA", data["image_prompt"], "photo")

    # 7. Solid color dark panel (y=470→1080, navy #050814, 73% opacity)
    #    + soft gradient overlay on top (feather=120, 38% opacity)
    #    → replicates the improved template design
    log("Adding dark panel + gradient overlay...")
    panel_result = ps_create_pixel_layer("Panel oscuro")
    panel_id = find_layer_id(panel_result.get("layers", []), "Panel oscuro")
    if panel_id:
        ps_select_rectangle(
            panel_id,
            {"top": 470, "left": 0, "right": 1080, "bottom": 1080},
            feather=0
        )
        ps_fill_selection(panel_id, {"red": 5, "green": 8, "blue": 20}, opacity=100)
        _ps("setLayerProperties", {"layerId": panel_id, "layerOpacity": 73, "blendMode": "NORMAL"})

    ov_result = ps_create_pixel_layer("Overlay")
    ov_id = find_layer_id(ov_result.get("layers", []), "Overlay")
    if ov_id:
        ps_select_rectangle(
            ov_id,
            {"top": 370, "left": 0, "right": 1080, "bottom": 1080},
            feather=120
        )
        ps_fill_selection(ov_id, {"red": 0, "green": 0, "blue": 0}, opacity=100)
        _ps("setLayerProperties", {"layerId": ov_id, "layerOpacity": 38, "blendMode": "NORMAL"})

    # 8. Text layers (centered, HelveticaNeue Bold)
    log("Adding text layers...")
    ps_add_texts(data["title_l1"], data["title_l2"], data["bible_ref"])

    # 9. Save JPG
    safe_title = re.sub(r"[^\w]", "_", title)[:40].lower()
    date_str   = datetime.now().strftime("%Y%m%d")
    out_path   = str(OUTPUT_DIR / f"{date_str}_{safe_title}.jpg")
    log(f"Saving to {out_path}...")
    ps_save_as(out_path, "JPG")

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
