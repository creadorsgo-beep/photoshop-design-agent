import sys; sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import _eval

count = int(_eval("app.activeDocument.layers.length;"))
print(f"Layers: {count}")
for i in range(count):
    name = _eval(f"app.activeDocument.layers[{i}].name;")
    op = _eval(f"app.activeDocument.layers[{i}].opacity;")
    b0 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[0].as('px'));")
    b1 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[1].as('px'));")
    b2 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[2].as('px'));")
    b3 = _eval(f"Math.round(app.activeDocument.layers[{i}].bounds[3].as('px'));")
    print(f"  [{i}] {name} op={op} bounds=[{b0},{b1},{b2},{b3}]")
