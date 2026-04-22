"""
Add Grupo Habitar logo to the historia and export as JPG + PNG.
"""
import sys, os, time, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import comtypes.client
import win32gui, win32con, win32api

LOGO_PATH = r"//ASUSAGU/Freelance/grupo habitar/blanco-Logo-grupo-habitar.png"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
OUTPUT_PNG = os.path.abspath(os.path.join(OUTPUT_DIR, 'habitar-historia-futuro.png'))
OUTPUT_JPG = os.path.abspath(os.path.join(OUTPUT_DIR, 'habitar-historia-futuro.jpg'))

os.makedirs(OUTPUT_DIR, exist_ok=True)

def dismiss_ps_dialogs(stop_event, duration=12):
    """Click 'No modificar' radio and OK on any Falta de perfil PS dialog."""
    deadline = time.time() + duration
    while not stop_event.is_set() and time.time() < deadline:
        def enum_cb(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if 'perfil' in title.lower() or 'color' in title.lower() or 'profile' in title.lower():
                # Find radio button "No modificar" and OK
                def child_cb(child, data):
                    txt = win32gui.GetWindowText(child)
                    if 'no modificar' in txt.lower() or 'don\'t color manage' in txt.lower():
                        win32api.SendMessage(child, win32con.BM_CLICK, 0, 0)
                        time.sleep(0.2)
                    if txt.strip().upper() in ('OK', 'ACEPTAR'):
                        data.append(child)
                ok_buttons = []
                win32gui.EnumChildWindows(hwnd, child_cb, ok_buttons)
                if ok_buttons:
                    win32api.SendMessage(ok_buttons[-1], win32con.BM_CLICK, 0, 0)
        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass
        time.sleep(0.3)


def _eval(app, jsx):
    return app.DoJavaScript(jsx.strip())


def main():
    app = comtypes.client.CreateObject('Photoshop.Application')

    # Find target doc
    doc = None
    for i in range(app.documents.count):
        if app.documents[i].name == "habitar-historia-futuro":
            doc = app.documents[i]
            break
    if doc is None:
        print("ERROR: Document 'habitar-historia-futuro' not found")
        return

    # Make it active
    app.activeDocument = doc
    print(f"Active doc: {doc.name}")

    # --- STEP 1: Add logo ---
    print("LOGO: Abriendo archivo...")
    stop_ev = threading.Event()
    t = threading.Thread(target=dismiss_ps_dialogs, args=(stop_ev, 15))
    t.daemon = True
    t.start()

    logo_jsx = f"""
var logoPath = "{LOGO_PATH.replace(chr(92), '/')}";
var logoFile = new File(logoPath);
var logoDoc = app.open(logoFile);
logoDoc.name;
"""
    try:
        logo_name = _eval(app, logo_jsx)
        print(f"LOGO: Abierto: {logo_name}")
    except Exception as e:
        stop_ev.set()
        print(f"LOGO: Error al abrir: {e}")
        # Try with backslashes
        logo_path_win = LOGO_PATH.replace('/', '\\')
        logo_jsx2 = f"""
var logoFile = new File("{logo_path_win.replace(chr(92), chr(92)+chr(92))}");
var logoDoc = app.open(logoFile);
logoDoc.name;
"""
        try:
            logo_name = _eval(app, logo_jsx2)
            print(f"LOGO: Abierto (intento 2): {logo_name}")
        except Exception as e2:
            print(f"LOGO: Error definitivo: {e2}")
            return
    finally:
        time.sleep(1)
        stop_ev.set()

    print("LOGO: Copiando contenido...")
    copy_jsx = """
var logoDoc = app.activeDocument;
logoDoc.selection.selectAll();
logoDoc.selection.copy();
var logoW = logoDoc.width;
var logoH = logoDoc.height;
logoDoc.close(SaveOptions.DONOTSAVECHANGES);
logoW + "x" + logoH;
"""
    try:
        dims = _eval(app, copy_jsx)
        print(f"LOGO: Dimensiones originales: {dims}")
    except Exception as e:
        print(f"LOGO: Error copiando: {e}")
        return

    print("LOGO: Pegando en historia...")
    app.activeDocument = doc

    paste_jsx = """
var doc = app.activeDocument;
doc.paste();
var newLayer = doc.activeLayer;
newLayer.name = "logo-grupo-habitar";

// Scale to ~380px wide centered
var bounds = newLayer.bounds;
var currentW = bounds[2] - bounds[0];
var targetW = 380;
var scale = (targetW / currentW) * 100;
newLayer.resize(scale, scale, AnchorPosition.MIDDLECENTER);

// Reposition: centered X, near bottom Y ~1760
bounds = newLayer.bounds;
var layerW = bounds[2] - bounds[0];
var layerH = bounds[3] - bounds[1];
var targetX = (1080 - layerW) / 2;
var targetY = 1720 - layerH / 2;
var dx = targetX - bounds[0];
var dy = targetY - bounds[1];
newLayer.translate(dx, dy);
newLayer.name;
"""
    try:
        result = _eval(app, paste_jsx)
        print(f"LOGO: Capa creada: {result}")
    except Exception as e:
        print(f"LOGO: Error pegando/posicionando: {e}")
        return

    # --- STEP 2: Export as PNG ---
    print("EXPORT: Guardando PNG...")
    png_path = OUTPUT_PNG.replace('\\', '/')
    export_png_jsx = f"""
var doc = app.activeDocument;
var pngFile = new File("{png_path}");
var pngOpts = new ExportOptionsSaveForWeb();
pngOpts.format = SaveDocumentType.PNG;
pngOpts.PNG8 = false;
pngOpts.quality = 100;
doc.exportDocument(pngFile, ExportType.SAVEFORWEB, pngOpts);
"PNG_OK";
"""
    try:
        r = _eval(app, export_png_jsx)
        print(f"EXPORT: PNG → {OUTPUT_PNG} ({r})")
    except Exception as e:
        print(f"EXPORT: Error PNG: {e}")

    # --- STEP 3: Export as JPG ---
    print("EXPORT: Guardando JPG...")
    jpg_path = OUTPUT_JPG.replace('\\', '/')
    export_jpg_jsx = f"""
var doc = app.activeDocument;
var jpgFile = new File("{jpg_path}");
var jpgOpts = new JPEGSaveOptions();
jpgOpts.quality = 10;
jpgOpts.formatOptions = FormatOptions.STANDARDBASELINE;
jpgOpts.matte = MatteType.NONE;
var flat = doc.duplicate();
flat.flatten();
flat.saveAs(jpgFile, jpgOpts, true, Extension.LOWERCASE);
flat.close(SaveOptions.DONOTSAVECHANGES);
"JPG_OK";
"""
    try:
        r = _eval(app, export_jpg_jsx)
        print(f"EXPORT: JPG → {OUTPUT_JPG} ({r})")
    except Exception as e:
        print(f"EXPORT: Error JPG: {e}")

    print("DONE")


if __name__ == '__main__':
    main()
