"""
Generates a custom .ico and a Windows desktop shortcut
for the YouTube Daily Post automation.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).parent.parent
ICON_PATH   = PROJECT_DIR / "assets" / "daily_post.ico"
BAT_PATH    = PROJECT_DIR / "scripts" / "run_daily_post.bat"
DESKTOP     = Path(os.environ["USERPROFILE"]) / "Desktop"
SHORTCUT    = DESKTOP / "100Biblia - Post Diario.lnk"


def make_icon():
    """Creates a multi-size .ico with a clean dark red + play symbol design."""
    ICON_PATH.parent.mkdir(exist_ok=True)
    sizes = [256, 128, 64, 48, 32, 16]
    frames = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle — dark crimson
        margin = int(size * 0.04)
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(180, 20, 20, 255)
        )

        # Inner lighter circle (ring effect)
        ring = int(size * 0.08)
        draw.ellipse(
            [ring, ring, size - ring, size - ring],
            fill=(210, 35, 35, 255)
        )

        # Play triangle (▶) — white, centered
        cx, cy = size // 2, size // 2
        half = int(size * 0.28)
        offset = int(size * 0.06)   # shift right slightly for optical center
        triangle = [
            (cx - half + offset, cy - half),
            (cx - half + offset, cy + half),
            (cx + half + offset, cy),
        ]
        draw.polygon(triangle, fill=(255, 255, 255, 240))

        # Small cross at top-right corner — white
        cross_r   = int(size * 0.13)
        cross_x   = int(size * 0.74)
        cross_y   = int(size * 0.20)
        cross_w   = max(2, int(size * 0.06))
        # vertical bar
        draw.rectangle([cross_x - cross_w // 2, cross_y - cross_r,
                        cross_x + cross_w // 2, cross_y + cross_r], fill=(255, 255, 200, 220))
        # horizontal bar
        draw.rectangle([cross_x - cross_r, cross_y - cross_w // 2,
                        cross_x + cross_r, cross_y + cross_w // 2], fill=(255, 255, 200, 220))

        frames.append(img)

    frames[0].save(
        str(ICON_PATH),
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print(f"Icon created: {ICON_PATH}")


def make_shortcut():
    """Creates a Windows .lnk shortcut using WScript.Shell via PowerShell."""
    icon_str = str(ICON_PATH).replace("/", "\\")
    bat_str  = str(BAT_PATH).replace("/", "\\")
    lnk_str  = str(SHORTCUT).replace("/", "\\")
    work_dir = str(PROJECT_DIR).replace("/", "\\")

    ps = f"""
$ws  = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut('{lnk_str}')
$lnk.TargetPath       = '{bat_str}'
$lnk.WorkingDirectory = '{work_dir}'
$lnk.IconLocation     = '{icon_str},0'
$lnk.Description      = '100% Biblia - Genera el post diario de Instagram desde YouTube'
$lnk.WindowStyle      = 7
$lnk.Save()
Write-Host 'Shortcut created.'
"""
    import subprocess
    result = subprocess.run(
        ["powershell", "-Command", ps],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Shortcut created: {SHORTCUT}")
    else:
        print(f"Error creating shortcut: {result.stderr}")


if __name__ == "__main__":
    make_icon()
    make_shortcut()
    print("\nDone. Check your Desktop for '100Biblia - Post Diario'")
