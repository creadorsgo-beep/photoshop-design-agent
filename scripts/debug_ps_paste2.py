"""Debug PS paste approach - isolated steps."""
import sys, time
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import _eval, create_document, set_background_color

BG = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\flow_gallery\flow_00.jpg"
BG_JSX = BG.replace("\\", "/")

print("Step 1: Create doc")
create_document("test-paste2", 1080, 1920, 72)
time.sleep(1)

print("Step 2: Check doc")
r = _eval("app.activeDocument.name;")
print("  ->", r)

print("Step 3: Save ref and open src")
try:
    jsx3 = f"""
var targetDoc = app.activeDocument;
var srcFile = new File("{BG_JSX}");
srcFile.exists + ' | ' + srcFile.fsName;
"""
    r = _eval(jsx3)
    print("  -> File check:", r)
except Exception as e:
    print("  ERROR:", e)

print("Step 4: Open file")
try:
    jsx4 = f"""
var srcFile = new File("{BG_JSX}");
var srcDoc = app.open(srcFile);
srcDoc.name + ' ' + srcDoc.width.as('px') + 'x' + srcDoc.height.as('px');
"""
    r = _eval(jsx4)
    print("  -> Opened:", r)
except Exception as e:
    print("  ERROR:", e)

print("Step 5: Flatten and copy from src doc")
try:
    jsx5 = """
var srcDoc = app.activeDocument;
srcDoc.flatten();
srcDoc.selection.selectAll();
srcDoc.selection.copy();
'copied from ' + srcDoc.name;
"""
    r = _eval(jsx5)
    print("  ->", r)
except Exception as e:
    print("  ERROR:", e)

print("Step 6: Close src and check docs count")
try:
    r = _eval("app.documents.length + ' docs open';")
    print("  -> Docs:", r)
    # Get the target doc (index 0 = first opened)
    r2 = _eval("""
var names = [];
for (var i=0; i<app.documents.length; i++) {
    names.push(app.documents[i].name);
}
names.join(', ');
""")
    print("  -> All docs:", r2)
except Exception as e:
    print("  ERROR:", e)

print("Step 7: Close src")
try:
    # Close the newly opened source doc
    r = _eval("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); 'closed';")
    print("  ->", r)
except Exception as e:
    print("  ERROR:", e)

print("Step 8: Check active doc")
try:
    r = _eval("app.activeDocument.name;")
    print("  -> Active:", r)
except Exception as e:
    print("  ERROR:", e)

print("Step 9: Paste")
try:
    r = _eval("app.activeDocument.paste(); 'pasted';")
    print("  ->", r)
except Exception as e:
    print("  ERROR:", e)

print("Done!")
