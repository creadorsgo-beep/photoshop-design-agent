"""
Diseño Palau - sistema responsivo.
El rectángulo verde se adapta al ancho/alto del texto con padding interno.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.ps_executor import (
    _eval, _jsx_string,
    place_image_as_background, place_image_at,
    apply_drop_shadow, save_as_psd, export_as_png,
    get_document_info,
)

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO    = os.path.join(BASE, "assets", "palau-logo.png").replace("\\", "/")
FOTO    = os.path.join(BASE, "assets", "cafe-fondo.jpg").replace("\\", "/")
OUT_PSD = os.path.join(BASE, "output", "se_vive_mejor_v5.psd").replace("\\", "/")
OUT_PNG = os.path.join(BASE, "output", "se_vive_mejor_v5.png").replace("\\", "/")

def step(msg):
    print(f">> {msg}")

# ── Cerrar documentos anteriores ──────────────────────────────────────────
step("Cerrando documentos anteriores...")
_eval("while(app.documents.length > 0){ app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); } 'ok';")

# ── Crear documento ───────────────────────────────────────────────────────
step("Creando documento 1080x1920...")
_eval('app.documents.add(1080,1920,72,"se_vive_mejor_v5",NewDocumentMode.RGB,DocumentFill.WHITE); "ok";')

# ── Foto de fondo (abrir, copiar, pegar — sin diálogos) ──────────────────
step("Colocando foto de fondo...")
foto_escaped = _jsx_string(FOTO)
_eval(f"""
app.displayDialogs = DialogModes.NO;
var mainDoc = app.activeDocument;
var srcDoc  = app.open(new File("{foto_escaped}"));
srcDoc.selection.selectAll();
srcDoc.selection.copy();
srcDoc.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument = mainDoc;
var pasted = mainDoc.paste();
pasted.name = "Foto_fondo";

// Escalar para cubrir el canvas (cover)
var cW = mainDoc.width.as('px');
var cH = mainDoc.height.as('px');
var b  = pasted.bounds;
var iW = b[2].as('px') - b[0].as('px');
var iH = b[3].as('px') - b[1].as('px');
var sc = Math.max(cW/iW, cH/iH) * 100;
pasted.resize(sc, sc, AnchorPosition.MIDDLECENTER);

// Centrar
var nb   = pasted.bounds;
var nlW  = nb[2].as('px') - nb[0].as('px');
var nlH  = nb[3].as('px') - nb[1].as('px');
pasted.translate((cW-nlW)/2 - nb[0].as('px'), (cH-nlH)/2 - nb[1].as('px'));
pasted.moveToEnd();
"ok";
""")

# ── Diseño responsivo: texto + rectángulo adaptado ────────────────────────
# Todo en un solo bloque JSX para medir bounds reales y posicionar correctamente
step("Construyendo diseño responsivo...")

titulo_text    = "Se vive mejor"
subtitulo_text = "CON CAFE TODOS LOS DIAS"
font_name      = "AgenorNeue-SemiBold"
pad_x          = 55   # padding horizontal del rectángulo verde
pad_y          = 18   # padding vertical del rectángulo verde
gap_title_bar  = 28   # espacio entre título y barra verde

# Zona segura Instagram Stories (1080x1920):
#   Top safe:    250px (evitar UI perfil)
#   Bottom safe: 390px desde abajo = y:1530 (evitar botones CTA)
#   Sides safe:  108px (10% de 1080) → contenido entre x:108 y x:972

titulo_esc    = _jsx_string(titulo_text)
subtitulo_esc = _jsx_string(subtitulo_text)
font_esc      = _jsx_string(font_name)

_eval(f"""
var doc = app.activeDocument;
var canvasW = doc.width.as('px');
var canvasH = doc.height.as('px');

// ── 1. Agregar TÍTULO ──────────────────────────────────────────────────
var titleLyr = doc.artLayers.add();
titleLyr.kind = LayerKind.TEXT;
titleLyr.name = "Titulo";
var ti = titleLyr.textItem;
ti.contents = "{titulo_esc}";
ti.size = new UnitValue(150, "pt");
ti.justification = Justification.CENTER;
try {{ ti.font = "{font_esc}"; }} catch(e) {{ ti.font = "ArialMT"; }}
var tc = new SolidColor(); tc.rgb.red=255; tc.rgb.green=255; tc.rgb.blue=255;
ti.color = tc;
ti.tracking = -20;

// Zona segura Instagram Stories
var safeTop    = 250;   // px desde arriba
var safeBottom = 1530;  // px desde arriba (1920 - 390)
var safeSide   = 108;   // px desde cada lado

// Posicionar título: dentro de zona segura, tercio superior
// El bloque de texto (titulo + gap + barra) mide ~300px total
// Lo centramos verticalmente entre safeTop y el centro del canvas (~960)
var blockCenterY = safeTop + (960 - safeTop) * 0.45;  // ~455px desde arriba
// baseline titulo = blockCenterY - blockHeight/2 + capHeight
ti.position = [canvasW/2, blockCenterY];

// ── 2. Medir bounds del título ────────────────────────────────────────
var tb = titleLyr.bounds;
var titleBottom = tb[3].as('px');  // borde inferior del título

// ── 3. Agregar SUBTÍTULO (todo mayúsculas) ────────────────────────────
var subLyr = doc.artLayers.add();
subLyr.kind = LayerKind.TEXT;
subLyr.name = "Subtitulo";
var si = subLyr.textItem;
si.contents = "{subtitulo_esc}";
si.size = new UnitValue(150, "pt");
si.justification = Justification.CENTER;
try {{ si.font = "{font_esc}"; }} catch(e) {{ si.font = "ArialMT"; }}
si.color = tc;
si.tracking = -20;

// Posicionar subtítulo: debajo del título con gap + padding de la barra
// baseline del subtítulo = titleBottom + gap + pad_y + cap_height_approx
// Para ALL_CAPS la altura visible es ~70% del font_size en px
var capH = 150 * 0.70;
var subBaselineY = titleBottom + {gap_title_bar} + {pad_y} + capH;
si.position = [canvasW/2, subBaselineY];

// ── 4. Medir bounds del subtítulo ────────────────────────────────────
var sb  = subLyr.bounds;
var sLeft   = sb[0].as('px');
var sTop    = sb[1].as('px');
var sRight  = sb[2].as('px');
var sBottom = sb[3].as('px');
var sW = sRight - sLeft;
var sH = sBottom - sTop;

// ── 5. Crear rectángulo verde adaptado al subtítulo ───────────────────
var rX = sLeft  - {pad_x};
var rY = sTop   - {pad_y};
var rW = sW     + {pad_x} * 2;
var rH = sH     + {pad_y} * 2;

// Respetar margen lateral de zona segura (108px)
if (rX < {108}) {{ rX = {108}; rW = canvasW - {108}*2; }}

var rectLyr = doc.artLayers.add();
rectLyr.name = "Barra_verde";
var region = [[rX,rY],[rX+rW,rY],[rX+rW,rY+rH],[rX,rY+rH]];
doc.selection.select(region);
var col = new SolidColor();
col.rgb.red = 54; col.rgb.green = 69; col.rgb.blue = 29;  // #36451d
doc.selection.fill(col, ColorBlendMode.NORMAL, 100, false);
doc.selection.deselect();

// ── 6. Mover rectángulo detrás del subtítulo ─────────────────────────
rectLyr.moveAfter(subLyr);

"ok";
""")

# ── Logo Palau ────────────────────────────────────────────────────────────
step("Colocando logo Palau...")
# Logo centrado horizontalmente, dentro de zona segura inferior (max y:1530-120=1410)
logo_w, logo_h = 242, 120
logo_x = (1080 - logo_w) // 2   # 419
logo_y = 1530 - logo_h - 30     # 1380 — dentro de zona segura con 30px de margen
place_image_at(LOGO, x=logo_x, y=logo_y, width=logo_w, height=logo_h, layer_name="Palau_Logo")
apply_drop_shadow("Palau_Logo", opacity=45, distance=6, size=12)

# ── Exportar ──────────────────────────────────────────────────────────────
step("Guardando PSD...")
save_as_psd(OUT_PSD)

step("Exportando PNG...")
export_as_png(OUT_PNG)

print("\n✓ Diseño completado.")
print(f"  PSD: {OUT_PSD}")
print(f"  PNG: {OUT_PNG}")
