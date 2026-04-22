"""
Delete bad logo layer, re-open logo, paste & place correctly.
Strategy: paste goes to doc center (540,960); translate to y=1760 center.
"""
import comtypes.client, os, time, threading
import win32gui, win32con, win32api

LOGO_PATH = "//ASUSAGU/Freelance/grupo habitar/blanco-Logo-grupo-habitar.png"
OUTPUT_PNG = os.path.abspath(os.path.join("output", "habitar-historia-futuro.png"))
OUTPUT_JPG = os.path.abspath(os.path.join("output", "habitar-historia-futuro.jpg"))

app = comtypes.client.CreateObject('Photoshop.Application')
doc = None
for i in range(app.documents.count):
    if app.documents[i].name == "habitar-historia-futuro":
        doc = app.documents[i]
        break

app.activeDocument = doc

# 1. Delete existing logo layer
print("Borrando logo anterior...")
jsx_del = """
var doc = app.activeDocument;
for (var i = doc.layers.length - 1; i >= 0; i--) {
    if (doc.layers[i].name == "logo-grupo-habitar") {
        doc.layers[i].remove();
        "deleted";
        break;
    }
}
"done";
"""
print(app.DoJavaScript(jsx_del))

# 2. Dialog dismisser
def dismiss(stop_ev, dur=15):
    deadline = time.time() + dur
    while not stop_ev.is_set() and time.time() < deadline:
        def cb(hwnd, _):
            t = win32gui.GetWindowText(hwnd)
            if 'perfil' in t.lower() or 'profile' in t.lower() or 'color' in t.lower():
                def child_cb(c, data):
                    ct = win32gui.GetWindowText(c)
                    if 'no modificar' in ct.lower():
                        win32api.SendMessage(c, win32con.BM_CLICK, 0, 0)
                        time.sleep(0.2)
                    if ct.strip().upper() in ('OK','ACEPTAR'):
                        data.append(c)
                oks = []
                win32gui.EnumChildWindows(hwnd, child_cb, oks)
                if oks:
                    win32api.SendMessage(oks[-1], win32con.BM_CLICK, 0, 0)
        try:
            win32gui.EnumWindows(cb, None)
        except Exception:
            pass
        time.sleep(0.3)

stop_ev = threading.Event()
t = threading.Thread(target=dismiss, args=(stop_ev, 15))
t.daemon = True
t.start()

# 3. Open logo, copy, close
print("Abriendo logo...")
logo_jsx = 'var lf = new File("' + LOGO_PATH.replace("\\", "/") + '"); var ld = app.open(lf); ld.selection.selectAll(); ld.selection.copy(); var w=ld.width; var h=ld.height; ld.close(SaveOptions.DONOTSAVECHANGES); w + "x" + h;'
try:
    dims = app.DoJavaScript(logo_jsx)
    print("Logo dims:", dims)
except Exception as e:
    print("Error abriendo logo:", e)
    stop_ev.set()
    raise

time.sleep(0.5)
stop_ev.set()

# 4. Paste into doc and position
app.activeDocument = doc
print("Pegando y posicionando logo...")

# When pasting, PS places layer centered in canvas: center at (540, 960)
# We want logo center at (540, 1760) → dy = +800
# Scale from 1518px → 380px = 25.03%
jsx_place = """
var doc = app.activeDocument;
doc.paste();
var ly = doc.activeLayer;
ly.name = "logo-grupo-habitar";

// Scale to 380px wide
var b = ly.bounds;
var curW = b[2].value - b[0].value;
var scl = (380.0 / curW) * 100.0;
ly.resize(scl, scl, AnchorPosition.MIDDLECENTER);

// Translate from doc center (540,960) to bottom (540,1760)
// After paste+scale, center is at doc center
ly.translate(0, 800);

// Verify
b = ly.bounds;
"pos: " + Math.round(b[0].value) + "," + Math.round(b[1].value) + " -> " + Math.round(b[2].value) + "," + Math.round(b[3].value);
"""
result = app.DoJavaScript(jsx_place)
print("Logo positioned:", result)

# 5. Export PNG
print("Exportando PNG...")
png_fwd = OUTPUT_PNG.replace("\\", "/")
app.DoJavaScript(
    'var f=new File("' + png_fwd + '");'
    'var o=new ExportOptionsSaveForWeb();'
    'o.format=SaveDocumentType.PNG;o.PNG8=false;o.quality=100;'
    'app.activeDocument.exportDocument(f,ExportType.SAVEFORWEB,o);'
    '"ok";'
)
print("PNG exportado:", OUTPUT_PNG)

# 6. Export JPG
print("Exportando JPG...")
jpg_fwd = OUTPUT_JPG.replace("\\", "/")
app.DoJavaScript(
    'var f=new File("' + jpg_fwd + '");'
    'var o=new JPEGSaveOptions();o.quality=10;'
    'var flat=app.activeDocument.duplicate();flat.flatten();'
    'flat.saveAs(f,o,true,Extension.LOWERCASE);'
    'flat.close(SaveOptions.DONOTSAVECHANGES);'
    '"ok";'
)
print("JPG exportado:", OUTPUT_JPG)

# 7. Save PSD
print("Guardando PSD...")
psd_fwd = os.path.abspath(os.path.join("output", "habitar-historia-futuro.psd")).replace("\\", "/")
app.DoJavaScript(
    'var f=new File("' + psd_fwd + '");'
    'var o=new PhotoshopSaveOptions();o.embedColorProfile=true;o.layers=true;'
    'app.activeDocument.saveAs(f,o,true,Extension.LOWERCASE);'
    '"ok";'
)
print("PSD guardado")
print("DONE")
