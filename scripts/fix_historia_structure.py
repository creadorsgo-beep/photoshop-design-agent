"""
Fix: rounded card-bg, rounded pill franja, logo inside card.
Recreates card-bg and franja-celeste as vector shape layers with rounded corners.
"""
import comtypes.client, os, time

app = comtypes.client.CreateObject('Photoshop.Application')
doc = None
for i in range(app.documents.count):
    if app.documents[i].name == "habitar-historia-futuro":
        doc = app.documents[i]
        break
app.activeDocument = doc

# JSX helper: create a solid-color rounded-rect shape layer
MAKE_ROUNDED_RECT_FN = """
function makeRoundedRect(name, lft, top, rgt, btm, rad, cr, cg, cb) {
    var idMk = charIDToTypeID("Mk  ");
    var d1 = new ActionDescriptor();
    var r1 = new ActionReference();
    r1.putClass(stringIDToTypeID("contentLayer"));
    d1.putReference(charIDToTypeID("null"), r1);

    var d2 = new ActionDescriptor();

    var d3 = new ActionDescriptor();
    var dClr = new ActionDescriptor();
    dClr.putDouble(charIDToTypeID("Rd  "), cr);
    dClr.putDouble(charIDToTypeID("Grn "), cg);
    dClr.putDouble(charIDToTypeID("Bl  "), cb);
    d3.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), dClr);
    d2.putObject(charIDToTypeID("Type"), stringIDToTypeID("solidColorLayer"), d3);

    var dShp = new ActionDescriptor();
    dShp.putUnitDouble(charIDToTypeID("Top "), charIDToTypeID("#Pxl"), top);
    dShp.putUnitDouble(charIDToTypeID("Left"), charIDToTypeID("#Pxl"), lft);
    dShp.putUnitDouble(charIDToTypeID("Btom"), charIDToTypeID("#Pxl"), btm);
    dShp.putUnitDouble(charIDToTypeID("Rght"), charIDToTypeID("#Pxl"), rgt);
    dShp.putUnitDouble(stringIDToTypeID("topLeft"),     charIDToTypeID("#Pxl"), rad);
    dShp.putUnitDouble(stringIDToTypeID("topRight"),    charIDToTypeID("#Pxl"), rad);
    dShp.putUnitDouble(stringIDToTypeID("bottomLeft"),  charIDToTypeID("#Pxl"), rad);
    dShp.putUnitDouble(stringIDToTypeID("bottomRight"), charIDToTypeID("#Pxl"), rad);
    d2.putObject(charIDToTypeID("Shp "), stringIDToTypeID("roundedRectangle"), dShp);

    d1.putObject(charIDToTypeID("Usng"), stringIDToTypeID("contentLayer"), d2);
    executeAction(idMk, d1, DialogModes.NO);
    app.activeDocument.activeLayer.name = name;
}
"""

# ── 1. Delete old card-bg ──────────────────────────────────────────────────
print("1. Borrando card-bg y franja-celeste...")
jsx_del = MAKE_ROUNDED_RECT_FN + """
var doc = app.activeDocument;
for (var i = doc.layers.length - 1; i >= 0; i--) {
    var n = doc.layers[i].name;
    if (n === "card-bg" || n === "franja-celeste") {
        doc.layers[i].remove();
    }
}
// Also remove duplicate blob if any
var seen = {};
for (var j = doc.layers.length - 1; j >= 0; j--) {
    var ln = doc.layers[j].name;
    if (ln === "blob-superior-derecho") {
        if (seen[ln]) { doc.layers[j].remove(); }
        else { seen[ln] = true; }
    }
}
"deleted";
"""
print(app.DoJavaScript(jsx_del))

# ── 2. Create rounded card-bg ──────────────────────────────────────────────
# Card: x=60 to x=1020, y=90 to y=1870  radius=40  color=#0f2d5a
print("2. Creando card-bg redondeado...")
jsx_card = MAKE_ROUNDED_RECT_FN + """
var doc = app.activeDocument;
// Activate fondo-navy so new layer goes above it
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name === "fondo-navy") {
        doc.setActiveLayer(doc.layers[i]);
        break;
    }
}
makeRoundedRect("card-bg", 60, 90, 1020, 1870, 40, 15, 45, 90);

// Now move it AFTER (below) blob-inferior-izquierdo
var cardLy = doc.activeLayer;
for (var k = 0; k < doc.layers.length; k++) {
    if (doc.layers[k].name === "blob-inferior-izquierdo") {
        cardLy.move(doc.layers[k], ElementPlacement.PLACEAFTER);
        break;
    }
}
"card-bg created";
"""
print(app.DoJavaScript(jsx_card))

# ── 3. Create rounded franja (pill) ────────────────────────────────────────
# Pill: x=120 to x=960, y=1250 to y=1370  radius=60  color=#01babc
print("3. Creando franja-celeste redondeada (pill)...")
jsx_franja = MAKE_ROUNDED_RECT_FN + """
var doc = app.activeDocument;
// Activate foto-principal so new layer goes above it
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name === "foto-principal") {
        doc.setActiveLayer(doc.layers[i]);
        break;
    }
}
makeRoundedRect("franja-celeste", 120, 1258, 960, 1378, 60, 1, 186, 188);

// Move it BEFORE titulo-linea1 (above titles is wrong; it should be above foto below titles)
// Currently it was created above foto-principal which is correct
// Move AFTER titulo-linea1 so it sits below titles but above foto
var franjaLy = doc.activeLayer;
for (var k = 0; k < doc.layers.length; k++) {
    if (doc.layers[k].name === "titulo-linea1") {
        franjaLy.move(doc.layers[k], ElementPlacement.PLACEAFTER);
        break;
    }
}
"franja created";
"""
print(app.DoJavaScript(jsx_franja))

# ── 4. Fix logo position ───────────────────────────────────────────────────
# Card ends y=1870. Logo 380x123px → center at y=1800 → bounds y=1739-1862
print("4. Reposicionando logo dentro del recuadro...")
jsx_logo = """
var doc = app.activeDocument;
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name === "logo-grupo-habitar") {
        var ly = doc.layers[i];
        var b = ly.bounds;
        var layerW = b[2].value - b[0].value;
        var layerH = b[3].value - b[1].value;
        var curCX  = b[0].value + layerW / 2;
        var curCY  = b[1].value + layerH / 2;
        // Target: centered at x=540, y=1790
        var dx = 540 - curCX;
        var dy = 1790 - curCY;
        ly.translate(dx, dy);
        var nb = ly.bounds;
        "Logo: " + Math.round(nb[0].value) + "," + Math.round(nb[1].value)
                 + " -> " + Math.round(nb[2].value) + "," + Math.round(nb[3].value);
        break;
    }
}
"""
print(app.DoJavaScript(jsx_logo))

# ── 5. Verify layer order ──────────────────────────────────────────────────
print("5. Orden de capas:")
jsx_list = """
var doc = app.activeDocument;
var out = [];
for (var i = 0; i < doc.layers.length; i++) {
    out.push(doc.layers[i].name);
}
out.join("|");
"""
layers = app.DoJavaScript(jsx_list).split("|")
for i, l in enumerate(layers):
    print(f"  {i}: {l}")

# ── 6. Export preview ──────────────────────────────────────────────────────
print("6. Exportando PNG de preview...")
png_fwd = os.path.abspath(os.path.join("output","habitar-historia-futuro.png")).replace("\\","/")
app.DoJavaScript(
    'var f=new File("'+png_fwd+'");'
    'var o=new ExportOptionsSaveForWeb();'
    'o.format=SaveDocumentType.PNG;o.PNG8=false;o.quality=100;'
    'app.activeDocument.exportDocument(f,ExportType.SAVEFORWEB,o);'
    '"ok";'
)
print("DONE — PNG exportado")
