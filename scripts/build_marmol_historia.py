"""
Build Palau Historia: Empanadas arabes — marble background from Flow.
Each PS operation is a separate _eval() call (single big JSX blocks fail).
"""
import os, sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import (
    create_document, set_background_color,
    add_text_layer, add_rectangle, save_as_psd, _eval
)

W, H = 1080, 1920
BG_IMG = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\flow_gallery\flow_00.jpg"
LOGO   = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\assets\palau-logo.png"
PSD_OUT = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\palau-marmol-v1.psd"

BG_JSX   = BG_IMG.replace("\\", "/")
LOGO_JSX = LOGO.replace("\\", "/")
PSD_JSX  = PSD_OUT.replace("\\", "/")

WHITE = "#FFFFFF"
GREEN = "#3d4725"
CREAM = "#F5F0E8"

def save_psd():
    _eval(f'app.activeDocument.saveAs(new File("{PSD_JSX}"), new PhotoshopSaveOptions(), true);')
    time.sleep(1.5)
    print("   [PSD saved]")

def paste_image(file_jsx, layer_name):
    """Open file, copy its content, close it (PS reverts to prior doc), paste."""
    # Open → becomes active doc
    _eval(f'app.open(new File("{file_jsx}"));')
    time.sleep(0.5)
    # Flatten + copy from active (= source)
    _eval("app.activeDocument.flatten(); app.activeDocument.selection.selectAll(); app.activeDocument.selection.copy();")
    # Close source → PS switches back to previous active doc (= target)
    _eval("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
    time.sleep(0.3)
    # Paste into current active (= target)
    _eval("app.activeDocument.paste();")
    # Name the pasted layer
    _eval(f'app.activeDocument.activeLayer.name = "{layer_name}";')

print("=== Palau Marmol Historia ===\n")

# 0. Close stale test/marmol docs
print("0. Closing stale docs...")
_eval("""
for (var i = app.documents.length - 1; i >= 0; i--) {
    var d = app.documents[i];
    var n = d.name;
    if (n.indexOf('palau-marmol') != -1 || n.indexOf('test-') != -1) {
        d.close(SaveOptions.DONOTSAVECHANGES);
    }
}
""")
time.sleep(0.5)

# 1. Create canvas
print("1. Creating 1080x1920 canvas...")
create_document("palau-marmol-v1", W, H, 72)
time.sleep(1)
set_background_color("#111108")

# 2. Place BG image
print("2. Placing marble photo...")
paste_image(BG_JSX, "FONDO/Foto")
time.sleep(0.5)
# Deselect any floating selection, then scale if needed
_eval("app.activeDocument.selection.deselect();")
# Scale to fill 1080x1920 (use .as('px') for UnitValue math)
_eval("""
var doc = app.activeDocument;
var lyr = doc.activeLayer;
var bounds = lyr.bounds;
var imgW = bounds[2].as('px') - bounds[0].as('px');
var imgH = bounds[3].as('px') - bounds[1].as('px');
if (imgW < 1080 || imgH < 1920) {
    var scaleX = (1080 / imgW) * 100;
    var scaleY = (1920 / imgH) * 100;
    var scale = Math.max(scaleX, scaleY);
    lyr.resize(scale, scale, AnchorPosition.MIDDLECENTER);
}
bounds = lyr.bounds;
var cx = (bounds[0].as('px') + bounds[2].as('px')) / 2;
var cy = (bounds[1].as('px') + bounds[3].as('px')) / 2;
lyr.translate(540 - cx, 960 - cy);
lyr.moveToEnd();
""")
print("   Photo placed and scaled.")

# Checkpoint
save_psd()

# 3. Bottom overlay (text legibility)
print("3. Bottom overlay...")
_eval("""
var doc = app.activeDocument;
var lyr = doc.artLayers.add();
lyr.name = "OVERLAY/Bottom";
var region = [[0, 880], [1080, 880], [1080, 1920], [0, 1920]];
doc.selection.select(region);
var c = new SolidColor(); c.rgb.hexValue = "0d0d04";
doc.selection.fill(c);
doc.selection.deselect();
lyr.opacity = 78;
""")
time.sleep(0.3)

# 4. Top overlay (logo area)
print("4. Top overlay...")
_eval("""
var doc = app.activeDocument;
var lyr = doc.artLayers.add();
lyr.name = "OVERLAY/Top";
var region = [[0, 0], [1080, 0], [1080, 370], [0, 370]];
doc.selection.select(region);
var c = new SolidColor(); c.rgb.hexValue = "0d0d04";
doc.selection.fill(c);
doc.selection.deselect();
lyr.opacity = 55;
""")
time.sleep(0.3)

# Checkpoint
save_psd()

# 5. Logo
print("5. Placing logo...")
if os.path.exists(LOGO):
    paste_image(LOGO_JSX, "MARCA/Logo")
    _eval("""
var doc = app.activeDocument;
doc.selection.deselect();
var lyr = doc.activeLayer;
var bounds = lyr.bounds;
var curH = bounds[3].as('px') - bounds[1].as('px');
var scale = (180 / curH) * 100;
lyr.resize(scale, scale, AnchorPosition.MIDDLECENTER);
bounds = lyr.bounds;
var cx = (bounds[0].as('px') + bounds[2].as('px')) / 2;
var cy = (bounds[1].as('px') + bounds[3].as('px')) / 2;
lyr.translate(540 - cx, 305 - cy);
lyr.moveToBeginning(doc);
""")
    print("   Logo placed.")

# 6. Green pill badge
print("6. Brand pill...")
_eval("""
var doc = app.activeDocument;
var lyr = doc.artLayers.add();
lyr.name = "TEXTO/Pill";
var region = [[108, 1100], [395, 1100], [395, 1150], [108, 1150]];
doc.selection.select(region);
var c = new SolidColor(); c.rgb.hexValue = "3d4725";
doc.selection.fill(c);
doc.selection.deselect();
""")
add_text_layer("NUEVO EN PALAU", x=124, y=1100+34, font="AgenorNeue-SemiBold", size=16, color=WHITE, layer_name="TEXTO/PillText")
time.sleep(0.3)

# 7. Main title — Jalliestha
print("7. Main title...")
add_text_layer("Proba\nlo nuevo", x=108, y=1185, font="Jalliestha", size=118, color=WHITE, layer_name="TEXTO/Titulo")
time.sleep(0.5)

# 8. Subtitle
print("8. Subtitle...")
add_text_layer("Empanadas arabes", x=108, y=1435, font="AgenorNeue-SemiBold", size=40, color=CREAM, layer_name="TEXTO/Subtitulo")
time.sleep(0.3)

# 9. Description
print("9. Description...")
add_text_layer(
    "Rellenas de carne, especias y pinones.\nUna receta con historia.",
    x=108, y=1500, font="AgenorNeue-SemiBold", size=24, color="#AAAAAA",
    layer_name="TEXTO/Descripcion"
)
time.sleep(0.3)

# 10. CTA
print("10. CTA...")
add_text_layer("Disponibles ahora", x=108, y=1720, font="AgenorNeue-SemiBold", size=30, color=WHITE, layer_name="TEXTO/CTA")
# CTA underline
_eval("""
var doc = app.activeDocument;
var lyr = doc.artLayers.add();
lyr.name = "TEXTO/CTALine";
var region = [[108, 1760], [340, 1760], [340, 1764], [108, 1764]];
doc.selection.select(region);
var c = new SolidColor(); c.rgb.hexValue = "3d4725";
doc.selection.fill(c);
doc.selection.deselect();
""")
time.sleep(0.3)

# 11. Final save
print("\n11. Final PSD save...")
save_psd()
print(f"\n=== Done! Output: {PSD_OUT} ===")
