"""Fix issues in palau-marmol-v1: logo transparency, title newline, overlay, photo position."""
import sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import add_text_layer, _eval

LOGO = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\assets\palau-logo.png"
LOGO_JSX = LOGO.replace("\\", "/")
PSD_JSX = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/palau-marmol-v1.psd"

WHITE = "#FFFFFF"
CREAM = "#F5F0E8"

def save():
    _eval(f'app.activeDocument.saveAs(new File("{PSD_JSX}"), new PhotoshopSaveOptions(), true);')
    time.sleep(1.5)
    print("   [saved]")

r = _eval("app.activeDocument.name;")
print("Active:", r)

# 1. Fix title - use \r (carriage return) for Photoshop line breaks
print("1. Fixing title...")
_eval("""
var doc = app.activeDocument;
for (var i = doc.layers.length - 1; i >= 0; i--) {
    if (doc.layers[i].name == "TEXTO/Titulo") {
        doc.layers[i].remove(); break;
    }
}
""")
# Use \r for Photoshop paragraph break
title_text = "Proba\rlo nuevo"  # \r = CR = Photoshop line break
add_text_layer(title_text, x=108, y=1185, font_name="Jalliestha", font_size=118, color_hex=WHITE, layer_name="TEXTO/Titulo")
print("   Title re-added with \\r line break.")
time.sleep(0.3)

# 2. Fix logo - use Place (Smart Object, preserves PNG transparency)
print("2. Fixing logo (Smart Object)...")
_eval("""
var doc = app.activeDocument;
for (var i = doc.layers.length - 1; i >= 0; i--) {
    if (doc.layers[i].name == "MARCA/Logo") {
        doc.layers[i].remove(); break;
    }
}
""")
# Open PNG (without flattening = preserves transparency), copy, paste
_eval(f'app.open(new File("{LOGO_JSX}"));')
time.sleep(0.5)
# Copy without flattening - keeps alpha channel
_eval("app.activeDocument.selection.selectAll(); app.activeDocument.selection.copy();")
_eval("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
time.sleep(0.3)
_eval("app.activeDocument.paste();")
_eval('app.activeDocument.activeLayer.name = "MARCA/Logo";')
time.sleep(0.3)
# Scale and position
_eval("""
var doc = app.activeDocument;
doc.selection.deselect();
var lyr = doc.activeLayer;
var b = lyr.bounds;
var curH = b[3].as('px') - b[1].as('px');
var scale = (180 / curH) * 100;
lyr.resize(scale, scale, AnchorPosition.MIDDLECENTER);
b = lyr.bounds;
var cx = (b[0].as('px') + b[2].as('px')) / 2;
var cy = (b[1].as('px') + b[3].as('px')) / 2;
lyr.translate(540 - cx, 305 - cy);
lyr.moveToBeginning(doc);
""")
print("   Logo fixed.")
time.sleep(0.3)

# 3. Reduce overlay opacity + shift photo
print("3. Fixing overlay + photo position...")
_eval("""
var doc = app.activeDocument;
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name == "OVERLAY/Bottom") {
        doc.layers[i].opacity = 60;
    }
    if (doc.layers[i].name == "FONDO/Foto") {
        doc.layers[i].translate(0, -280);
    }
}
""")
print("   Overlay and photo adjusted.")

save()

# Export preview
print("Exporting preview...")
out = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/palau-marmol-v1.jpg"
_eval(f"""
var flat = app.activeDocument.duplicate();
flat.flatten();
var opts = new JPEGSaveOptions();
opts.quality = 10;
flat.saveAs(new File("{out}"), opts, true);
flat.close(SaveOptions.DONOTSAVECHANGES);
'done';
""")
print("=== Done! ===")
