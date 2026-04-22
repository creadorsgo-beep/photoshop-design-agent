"""Debug PS paste approach step by step."""
import sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import _eval, create_document, set_background_color

BG = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/flow_gallery/flow_00.jpg"

print("Step 1: Create doc")
create_document("test-paste", 1080, 1920, 72)
time.sleep(1)

print("Step 2: Check active doc")
r = _eval("app.activeDocument.name + ' w=' + app.activeDocument.width.as('px') + ' h=' + app.activeDocument.height.as('px');")
print("  Doc:", r)

print("Step 3: Open source and copy (without closing yet)")
jsx_open = f"""
var targetDoc = app.activeDocument;
var srcFile = new File("{BG}");
var srcDoc = app.open(srcFile);
var srcName = srcDoc.name;
var srcW = srcDoc.width.as('px');
var srcH = srcDoc.height.as('px');
srcName + ' ' + srcW + 'x' + srcH;
"""
r = _eval(jsx_open)
print("  Src doc:", r)

print("Step 4: Copy from source")
r = _eval("""
var srcDoc = app.activeDocument;
srcDoc.flatten();
srcDoc.selection.selectAll();
srcDoc.selection.copy();
'copied';
""")
print("  Copy:", r)

print("Step 5: Switch to target and paste")
# First close the src doc
r = _eval("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); 'closed';")
print("  Closed src:", r)

# Check what's active now
r = _eval("app.activeDocument.name;")
print("  Active doc now:", r)

print("Step 6: Paste")
r = _eval("app.activeDocument.paste(); app.activeDocument.activeLayer.name;")
print("  Paste result:", r)

print("Done!")
