import sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import _eval

PSD_JSX = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/palau-marmol-v1.psd"

def save():
    _eval(f'app.activeDocument.saveAs(new File("{PSD_JSX}"), new PhotoshopSaveOptions(), true);')
    time.sleep(1.5)
    print("   [saved]")

count = int(_eval("app.activeDocument.layers.length;"))
print(f"Layers: {count}")
for i in range(count):
    name = _eval(f"app.activeDocument.layers[{i}].name;")
    b1 = int(float(_eval(f"app.activeDocument.layers[{i}].bounds[1].as('px');")))
    b3 = int(float(_eval(f"app.activeDocument.layers[{i}].bounds[3].as('px');")))
    print(f"  [{i}] {name} y={b1}-{b3}")

# Fix FONDO/Foto position: find by name
print("\nFixing photo position...")
for i in range(count):
    name = _eval(f"app.activeDocument.layers[{i}].name;")
    if "FONDO" in name:
        _eval(f"app.activeDocument.layers[{i}].translate(0, 200);")
        b1 = int(float(_eval(f"app.activeDocument.layers[{i}].bounds[1].as('px');")))
        b3 = int(float(_eval(f"app.activeDocument.layers[{i}].bounds[3].as('px');")))
        print(f"   {name} now y={b1}-{b3}")
        break

save()

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
print("Done!")
