"""
Agrega los elementos de diseño al documento Photoshop ya abierto.
No abre ni cierra archivos — trabaja sobre el documento activo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.ps_executor import (
    _eval, _jsx_string,
    place_image_at, apply_drop_shadow, save_as_psd, export_as_png,
    get_document_info,
)

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO    = os.path.join(BASE, "assets", "palau-logo.png").replace("\\", "/")
OUT_PSD = os.path.join(BASE, "output", "se_vive_mejor_v5.psd").replace("\\", "/")
OUT_PNG = os.path.join(BASE, "output", "se_vive_mejor_v5.png").replace("\\", "/")

def step(msg):
    print(f">> {msg}")

info = get_document_info()
print(f"Documento activo: {info['name']} {info['width']}x{info['height']}")
print(f"Capas existentes: {[l['name'] for l in info['layers']]}")

# ── Limpiar capas de diseño anteriores (mantener solo foto de fondo) ──────
step("Limpiando capas de diseño anteriores...")
_eval("""
var doc = app.activeDocument;
var keep = ['Foto_fondo'];
var toDelete = [];
for (var i = 0; i < doc.artLayers.length; i++) {
    var found = false;
    for (var k = 0; k < keep.length; k++) {
        if (doc.artLayers[i].name === keep[k]) { found = true; break; }
    }
    if (!found) toDelete.push(doc.artLayers[i]);
}
// También eliminar duplicados de Foto_fondo
var fotoCount = 0;
for (var i = 0; i < doc.artLayers.length; i++) {
    if (doc.artLayers[i].name === 'Foto_fondo') {
        fotoCount++;
        if (fotoCount > 1) toDelete.push(doc.artLayers[i]);
    }
}
for (var j = 0; j < toDelete.length; j++) {
    try { toDelete[j].remove(); } catch(e) {}
}
'ok';
""")

# ── Diseño responsivo en un solo bloque JSX ───────────────────────────────
step("Construyendo diseño responsivo con márgenes de zona segura...")

font_name      = "AgenorNeue-SemiBold"
titulo_text    = "Se vive mejor"
subtitulo_text = "CON CAFE TODOS LOS DIAS"
pad_x          = 55    # padding horizontal barra verde
pad_y          = 22    # padding vertical barra verde
gap            = 30    # espacio entre título y barra
safe_top       = 250   # zona segura superior Instagram Stories
safe_bottom    = 1530  # zona segura inferior Instagram Stories
safe_side      = 108   # margen lateral zona segura

font_esc  = _jsx_string(font_name)
title_esc = _jsx_string(titulo_text)
sub_esc   = _jsx_string(subtitulo_text)

result = _eval(f"""
var doc      = app.activeDocument;
var canvasW  = doc.width.as('px');
var canvasH  = doc.height.as('px');
var safeTop  = {safe_top};
var safeSide = {safe_side};
var padX     = {pad_x};
var padY     = {pad_y};
var gap      = {gap};

// Color blanco compartido
var white = new SolidColor();
white.rgb.red = 255; white.rgb.green = 255; white.rgb.blue = 255;

// ─── TÍTULO ───────────────────────────────────────────────────────────────
var titleLyr = doc.artLayers.add();
titleLyr.kind = LayerKind.TEXT;
titleLyr.name = "Titulo";
var ti = titleLyr.textItem;
ti.contents = "{title_esc}";
ti.size = new UnitValue(150, "pt");
ti.justification = Justification.CENTER;
try {{ ti.font = "{font_esc}"; }} catch(e) {{ ti.font = "ArialMT"; }}
ti.color = white;
ti.tracking = -20;

// Posición inicial: centrar x, y en zona segura superior (~38% del canvas)
ti.position = [canvasW / 2, safeTop + (canvasH * 0.38 - safeTop) * 0.8];

// Leer bounds reales del título
var tb      = titleLyr.bounds;
var titleB  = tb[3].as('px');  // borde inferior del texto del título

// ─── SUBTÍTULO (todo mayúsculas) ──────────────────────────────────────────
var subLyr = doc.artLayers.add();
subLyr.kind = LayerKind.TEXT;
subLyr.name = "Subtitulo";
var si = subLyr.textItem;
si.contents = "{sub_esc}";
si.size = new UnitValue(150, "pt");
si.justification = Justification.CENTER;
try {{ si.font = "{font_esc}"; }} catch(e) {{ si.font = "ArialMT"; }}
si.color = white;
si.tracking = -20;

// Baseline del subtítulo = borde inferior título + gap + padding + capHeight
var capH       = 150 * 0.68;
var subBaseline = titleB + gap + padY + capH;
si.position = [canvasW / 2, subBaseline];

// Leer bounds reales del subtítulo
var sb   = subLyr.bounds;
var sL   = sb[0].as('px');
var sT   = sb[1].as('px');
var sR   = sb[2].as('px');
var sBot = sb[3].as('px');

// ─── RECTÁNGULO VERDE RESPONSIVO ──────────────────────────────────────────
// Se adapta al ancho real del texto + padding
var rX = sL - padX;
var rY = sT - padY;
var rW = (sR - sL) + padX * 2;
var rH = (sBot - sT) + padY * 2;

// Respetar margen lateral de zona segura
if (rX < safeSide) {{
    rX = safeSide;
    rW = canvasW - safeSide * 2;
}}

var rectLyr = doc.artLayers.add();
rectLyr.name = "Barra_verde";
var region  = [[rX, rY], [rX+rW, rY], [rX+rW, rY+rH], [rX, rY+rH]];
doc.selection.select(region);
var green = new SolidColor();
green.rgb.red = 54; green.rgb.green = 69; green.rgb.blue = 29;
doc.selection.fill(green, ColorBlendMode.NORMAL, 100, false);
doc.selection.deselect();

// Mover rectángulo detrás del subtítulo
rectLyr.moveAfter(subLyr);

// Retornar dimensiones para debug
'titulo_bottom:' + Math.round(titleB) + ' sub_top:' + Math.round(sT) +
' rect_x:' + Math.round(rX) + ' rect_y:' + Math.round(rY) +
' rect_w:' + Math.round(rW) + ' rect_h:' + Math.round(rH);
""")
print(f"   Layout: {result}")

# ── Logo Palau centrado, dentro de zona segura inferior ───────────────────
step("Colocando logo Palau...")
logo_w, logo_h = 242, 120
logo_x = (1080 - logo_w) // 2
logo_y = safe_bottom - logo_h - 40
place_image_at(LOGO, x=logo_x, y=logo_y, width=logo_w, height=logo_h, layer_name="Palau_Logo")
apply_drop_shadow("Palau_Logo", opacity=45, distance=6, size=12)

# ── Exportar ──────────────────────────────────────────────────────────────
step("Guardando PSD...")
save_as_psd(OUT_PSD)

step("Exportando PNG...")
export_as_png(OUT_PNG)

print(f"\n✓ Listo: {OUT_PNG}")
