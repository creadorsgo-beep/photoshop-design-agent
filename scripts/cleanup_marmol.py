"""Clean up duplicate layers and fix positions in palau-marmol-v1."""
import sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import _eval

PSD_JSX = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/palau-marmol-v1.psd"

def save():
    _eval(f'app.activeDocument.saveAs(new File("{PSD_JSX}"), new PhotoshopSaveOptions(), true);')
    time.sleep(1.5)
    print("   [saved]")

# Remove unwanted/duplicate layers by index (from bottom to top to preserve indices)
# Layers to remove: [2] palau-logo, [11] TEXTO/Pill dup, [12] OVERLAY/Top dup, [13] OVERLAY/Bottom dup
# Remove from highest index to lowest
for idx in [13, 12, 11, 2]:
    r = _eval(f"app.activeDocument.layers[{idx}].name;")
    print(f"Removing [{idx}]: {r}")
    _eval(f"app.activeDocument.layers[{idx}].remove();")
    time.sleep(0.2)

# Verify
count = int(_eval("app.activeDocument.layers.length;"))
print(f"\nLayers after cleanup: {count}")
for i in range(count):
    name = _eval(f"app.activeDocument.layers[{i}].name;")
    b1 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[1].as('px'));")
    b3 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[3].as('px'));")
    print(f"  [{i}] {name} y={b1}-{b3}")

# Fix FONDO/Foto: shift back up by +200 (undo some of the -280 shift)
# Current: -286 to 1649. After +200: -86 to 1849 (covers canvas better)
print("\nFixing photo position...")
fondo_idx = None
for i in range(count):
    name = _eval(f"app.activeDocument.layers[{i}].name;")
    if name == "FONDO/Foto":
        fondo_idx = i
        break
if fondo_idx is not None:
    _eval(f"app.activeDocument.layers[{fondo_idx}].translate(0, 200);")
    b1 = _eval(f"Math.round(app.activeDocument.layers[{fondo_idx}].bounds[1].as('px'));")
    b3 = _eval(f"Math.round(app.activeDocument.layers[{fondo_idx}].bounds[3].as('px'));")
    print(f"   FONDO/Foto now: y={b1}-{b3}")

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
