"""
Build Palau Instagram Story: "Proba lo nuevo / EMPANADAS ÁRABES"
- PS Object Selection to cut out plate from background
- Pillow: composite plate on verde canvas + gradient
- PS: text layers, pills, logo
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import photoshop.api as ps

# --- Paths ---
PHOTO_SRC  = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\empanadas01.jpg"
LOGO_SRC   = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\assets\palau-logo.png"
CUTOUT_OUT = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\_emp01_cutout.png"
BG_OUT     = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\palau_emp_bg.png"
FINAL_OUT  = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\palau-proba-lo-nuevo.png"

CANVAS_W, CANVAS_H = 1080, 1920
VERDE     = (61, 71, 37)   # #3d4725
VERDE_HEX = "#3d4725"

# Safe zone
SZ_X_MIN, SZ_X_MAX = 65, 1015
SZ_Y_TOP, SZ_Y_BOT = 250, 1670


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _app():
    return ps.Application()

def _eval(jsx):
    app = _app()
    if hasattr(app, 'DoJavaScript'):
        return app.DoJavaScript(jsx.strip())
    return app.eval_(jsx.strip())

def jstr(s):
    return json.dumps(s)[1:-1]

def rgb(h):
    h = h.lstrip('#')
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)


# ---------------------------------------------------------------------------
# Step 1: PS — open photo, Select Subject, delete background, export PNG
# ---------------------------------------------------------------------------

def extract_subject_ps():
    print("  Closing open PS documents...")
    _eval('app.displayDialogs = DialogModes.NO; while(app.documents.length>0){ app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); }')

    src = PHOTO_SRC.replace('\\', '/')
    out = CUTOUT_OUT.replace('\\', '/')

    jsx = f"""
    // Open source photo
    var srcFile = new File("{jstr(src)}");
    var doc = app.open(srcFile);
    app.activeDocument = doc;

    // Flatten and unlock background layer
    doc.flatten();
    doc.artLayers[0].isBackgroundLayer = false;

    // Remove Background (Adobe Sensei AI — PS 2021+)
    executeAction(stringIDToTypeID("removeBackground"), new ActionDescriptor(), DialogModes.NO);

    // Apply any layer masks so transparency is baked in
    var layer = doc.artLayers[0];
    if (layer.layerMaskLinked !== undefined) {{
        try {{
            var idApplyMask = stringIDToTypeID("applyMask");
            var maskDesc = new ActionDescriptor();
            maskDesc.putBoolean(stringIDToTypeID("delete"), false);
            executeAction(idApplyMask, maskDesc, DialogModes.NO);
        }} catch(e) {{}}
    }}

    // Export PNG with transparency
    var exportOpts = new ExportOptionsSaveForWeb();
    exportOpts.format = SaveDocumentType.PNG;
    exportOpts.PNG8 = false;
    exportOpts.transparency = true;
    exportOpts.quality = 100;
    doc.exportDocument(new File("{jstr(out)}"), ExportType.SAVEFORWEB, exportOpts);

    doc.close(SaveOptions.DONOTSAVECHANGES);
    "done";
    """
    result = _eval(jsx)
    print(f"  PS cutout result: {result}")
    return CUTOUT_OUT


# ---------------------------------------------------------------------------
# Step 2: Pillow — composite cutout on verde canvas
# ---------------------------------------------------------------------------

def build_background(cutout_path):
    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (*VERDE, 255))

    # Load plate cutout
    plate = Image.open(cutout_path).convert('RGBA')

    # Scale: plate occupies ~900px wide, placed in lower portion
    orig_w, orig_h = plate.size
    target_w = 980
    target_h = int(orig_h * (target_w / orig_w))
    plate = plate.resize((target_w, target_h), Image.LANCZOS)

    # Position: horizontally centered, bottom-anchored with small margin
    px = (CANVAS_W - target_w) // 2
    py = CANVAS_H - target_h - 40

    # Subtle drop shadow
    shadow_alpha = plate.split()[3]
    shadow_layer = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0,0,0,0))
    shadow_img = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
    shadow_img.putalpha(shadow_alpha)
    shadow_blurred = shadow_img.filter(ImageFilter.GaussianBlur(radius=20))
    arr = np.array(shadow_blurred)
    arr[...,0] = 0; arr[...,1] = 0; arr[...,2] = 0
    arr[...,3] = (arr[...,3].astype(float) * 0.5).astype(np.uint8)
    shadow_final = Image.fromarray(arr)
    canvas.alpha_composite(shadow_final, (px, py + 15))

    # Paste cutout
    canvas.alpha_composite(plate, (px, py))

    # Gradient fade: verde top → transparent, over photo top edge
    grad_h = 380
    grad_y = max(py - 80, 0)
    arr_g = np.zeros((grad_h, CANVAS_W, 4), dtype=np.uint8)
    for y in range(grad_h):
        a = int(255 * (1 - y / grad_h) ** 1.5)
        arr_g[y, :] = [VERDE[0], VERDE[1], VERDE[2], a]
    canvas.alpha_composite(Image.fromarray(arr_g, 'RGBA'), (0, grad_y))

    # Logo
    try:
        logo = Image.open(LOGO_SRC).convert('RGBA')
        lw = 220
        lh = int(logo.size[1] * (lw / logo.size[0]))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        canvas.alpha_composite(logo, ((CANVAS_W - lw)//2, 1540))
    except FileNotFoundError:
        print("  Logo not found")

    # Save as RGB
    result = Image.new('RGB', (CANVAS_W, CANVAS_H), VERDE)
    result.paste(canvas, mask=canvas.split()[3])
    result.save(BG_OUT, 'PNG')
    print(f"  Background saved: {BG_OUT}")
    return py  # plate top y


# ---------------------------------------------------------------------------
# Step 3: PS — add text, pills, export final
# ---------------------------------------------------------------------------

def add_text_ps():
    _eval('app.displayDialogs = DialogModes.NO; while(app.documents.length>0){ app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); }')

    bg = BG_OUT.replace('\\', '/')
    out = FINAL_OUT.replace('\\', '/')

    # Layout
    title_size   = 110
    title_y1     = 305 + title_size          # line 1 baseline
    title_y2     = title_y1 + 125            # line 2 baseline

    # Subtitle pill
    sub_pill_w   = 540
    sub_pill_h   = 90
    sub_pill_x   = (CANVAS_W - sub_pill_w) // 2   # 270
    sub_pill_y   = title_y2 + 28
    sub_text_x   = CANVAS_W // 2                   # centered on canvas
    sub_text_y   = sub_pill_y + sub_pill_h - 24    # baseline inside pill

    # "NEW" badge pill
    new_pill_w   = 118
    new_pill_h   = 62
    new_pill_x   = SZ_X_MAX - new_pill_w           # 897
    new_pill_y   = SZ_Y_TOP + 8                    # 258
    new_text_x   = new_pill_x + new_pill_w // 2
    new_text_y   = new_pill_y + new_pill_h - 18

    def text_layer(text, x, y, font, size, hex_c, align='CENTER', tracking=-20):
        r, g, b = rgb(hex_c)
        return f"""
        var tl = app.activeDocument.artLayers.add();
        tl.kind = LayerKind.TEXT;
        tl.name = "txt_{jstr(text[:20])}";
        var td = tl.textItem;
        td.contents = "{jstr(text)}";
        td.font = "{font}";
        td.size = new UnitValue({size}, "px");
        td.color.rgb.red = {r}; td.color.rgb.green = {g}; td.color.rgb.blue = {b};
        td.justification = Justification.{align};
        td.tracking = {tracking};
        td.position = [new UnitValue({x}, "px"), new UnitValue({y}, "px")];
        """

    def pill_layer(px, py, pw, ph, radius, hex_c):
        r, g, b = rgb(hex_c)
        # Build rounded rect selection via polygon approximation
        steps = 8
        pts = []
        corners = [
            (px + radius, py, px + pw - radius, py),
            (px + pw, py + radius, px + pw, py + ph - radius),
            (px + pw - radius, py + ph, px + radius, py + ph),
            (px, py + ph - radius, px, py + radius),
        ]
        lines = [
            f"[new UnitValue({px+radius},'px'), new UnitValue({py},'px')]",
            f"[new UnitValue({px+pw-radius},'px'), new UnitValue({py},'px')]",
            f"[new UnitValue({px+pw},'px'), new UnitValue({py+radius},'px')]",
            f"[new UnitValue({px+pw},'px'), new UnitValue({py+ph-radius},'px')]",
            f"[new UnitValue({px+pw-radius},'px'), new UnitValue({py+ph},'px')]",
            f"[new UnitValue({px+radius},'px'), new UnitValue({py+ph},'px')]",
            f"[new UnitValue({px},'px'), new UnitValue({py+ph-radius},'px')]",
            f"[new UnitValue({px},'px'), new UnitValue({py+radius},'px')]",
        ]
        sel = "[" + ", ".join(lines) + "]"
        return f"""
        var pl = app.activeDocument.artLayers.add();
        pl.name = "pill_{px}_{py}";
        app.activeDocument.selection.select({sel});
        var pc = new SolidColor();
        pc.rgb.red={r}; pc.rgb.green={g}; pc.rgb.blue={b};
        app.activeDocument.selection.fill(pc);
        app.activeDocument.selection.deselect();
        """

    jsx = f"""
    var doc = app.open(new File("{jstr(bg)}"));
    app.activeDocument = doc;

    // Subtitle pill (beige)
    {pill_layer(sub_pill_x, sub_pill_y, sub_pill_w, sub_pill_h, 45, "#dfdace")}

    // NEW badge pill (white)
    {pill_layer(new_pill_x, new_pill_y, new_pill_w, new_pill_h, 31, "#ffffff")}

    // Title lines
    {text_layer("Proba lo", CANVAS_W//2, title_y1, "AgenorNeue-SemiBold", title_size, "#ffffff")}
    {text_layer("nuevo", CANVAS_W//2, title_y2, "AgenorNeue-SemiBold", title_size, "#ffffff")}

    // Subtitle text centered in pill
    {text_layer("EMPANADAS ÁRABES", sub_text_x, sub_text_y, "AgenorNeue-SemiBold", 48, "#3d4725", "CENTER", -20)}

    // NEW text centered in badge
    {text_layer("NEW", new_text_x, new_text_y, "AgenorNeue-SemiBold", 36, "#3d4725", "CENTER", -20)}

    // Export
    var eo = new ExportOptionsSaveForWeb();
    eo.format = SaveDocumentType.PNG;
    eo.PNG8 = false;
    eo.quality = 100;
    doc.exportDocument(new File("{jstr(out)}"), ExportType.SAVEFORWEB, eo);
    doc.close(SaveOptions.DONOTSAVECHANGES);
    "done";
    """
    result = _eval(jsx)
    print(f"  PS export result: {result}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Step 1: PS — extracting subject with Select Subject...")
    cutout = extract_subject_ps()

    print("Step 2: Pillow — compositing on verde canvas...")
    build_background(cutout)

    print("Step 3: PS — adding text and pills...")
    add_text_ps()

    print(f"\nFinal: {FINAL_OUT}")
