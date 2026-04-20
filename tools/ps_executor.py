"""
Controls Adobe Photoshop via COM automation (Windows only).
Uses photoshop-python-api + ExtendScript (JSX) eval for full PS control.

Photoshop must be installed. The first call opens PS if it isn't running.
All coordinates are in pixels. Colors are hex strings (#rrggbb).
"""

import json
import os
import photoshop.api as ps


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _app() -> ps.Application:
    return ps.Application()


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _jsx_string(text: str) -> str:
    """Escape text for safe embedding inside a JSX double-quoted string."""
    return json.dumps(text)[1:-1]  # strips surrounding " from json.dumps


def _eval(jsx: str) -> str:
    """Execute JSX in the running Photoshop instance."""
    app = _app()
    if hasattr(app, 'DoJavaScript'):
        return app.DoJavaScript(jsx.strip())
    return app.eval_(jsx.strip())


# ---------------------------------------------------------------------------
# Document operations
# ---------------------------------------------------------------------------

def create_document(name: str, width: int, height: int, resolution: int = 72) -> dict:
    """Create a new RGB Photoshop document."""
    app = _app()
    app.documents.add(width, height, resolution, name)
    return {"status": "created", "name": name, "width": width, "height": height}


def open_template(file_path: str) -> dict:
    """Open an existing PSD/JPG/PNG file in Photoshop, suppressing all dialogs."""
    app = _app()
    app.displayDialogs = 3  # DialogModes.NO — suppresses color profile and other dialogs
    file_path = file_path.replace("\\", "/")
    doc = app.open(file_path)
    return {
        "status": "opened",
        "name": doc.name,
        "width": int(doc.width),
        "height": int(doc.height),
    }


def get_document_info() -> dict:
    """Return dimensions and layer names of the active document."""
    app = _app()
    doc = app.activeDocument
    layers = []
    for i in range(doc.artLayers.length):
        lyr = doc.artLayers[i]
        layers.append({"name": lyr.name, "kind": str(lyr.kind), "visible": lyr.visible})
    return {
        "name": doc.name,
        "width": int(doc.width),
        "height": int(doc.height),
        "layers": layers,
    }


def save_as_psd(output_path: str) -> dict:
    """Save the active document as a PSD (copy, keeps current state)."""
    app = _app()
    doc = app.activeDocument
    output_path = output_path.replace("\\", "/")
    options = ps.PhotoshopSaveOptions()
    doc.saveAs(output_path, options, asCopy=True)
    return {"status": "saved", "output": output_path}


# ---------------------------------------------------------------------------
# Background & fills
# ---------------------------------------------------------------------------

def set_background_color(color_hex: str) -> dict:
    """Fill the background layer with a solid color."""
    r, g, b = _rgb(color_hex)
    jsx = f"""
    var doc = app.activeDocument;
    try {{ doc.backgroundLayer.locked = false; }} catch(e) {{}}
    var c = new SolidColor();
    c.rgb.red = {r}; c.rgb.green = {g}; c.rgb.blue = {b};
    app.foregroundColor = c;
    doc.selection.selectAll();
    doc.selection.fill(app.foregroundColor, ColorBlendMode.NORMAL, 100, false);
    doc.selection.deselect();
    'ok';
    """
    _eval(jsx)
    return {"status": "filled", "color": color_hex}


def add_gradient_background(
    color1_hex: str,
    color2_hex: str,
    angle: int = 90,
    layer_name: str = "Gradient Background",
) -> dict:
    """Add a new layer with a linear gradient from color1 to color2."""
    r1, g1, b1 = _rgb(color1_hex)
    r2, g2, b2 = _rgb(color2_hex)
    name_escaped = _jsx_string(layer_name)
    jsx = f"""
    var doc = app.activeDocument;
    var lyr = doc.artLayers.add();
    lyr.name = "{name_escaped}";
    doc.selection.selectAll();

    // Build gradient descriptor
    var gDesc = new ActionDescriptor();
    var gColorDesc = new ActionDescriptor();
    var stopList = new ActionList();

    function makeStop(r, g, b, loc) {{
        var stop = new ActionDescriptor();
        var col  = new ActionDescriptor();
        col.putDouble(charIDToTypeID("Rd  "), r);
        col.putDouble(charIDToTypeID("Grn "), g);
        col.putDouble(charIDToTypeID("Bl  "), b);
        stop.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), col);
        stop.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("Clry"), charIDToTypeID("UsrS"));
        stop.putInteger(charIDToTypeID("Lctn"), loc);
        stop.putInteger(charIDToTypeID("Mdpn"), 50);
        return stop;
    }}
    stopList.putObject(charIDToTypeID("Clrt"), makeStop({r1},{g1},{b1},0));
    stopList.putObject(charIDToTypeID("Clrt"), makeStop({r2},{g2},{b2},4096));

    gColorDesc.putList(charIDToTypeID("Clrs"), stopList);
    gColorDesc.putEnumerated(charIDToTypeID("GrdT"), charIDToTypeID("GrdT"), charIDToTypeID("CStr"));
    gColorDesc.putString(charIDToTypeID("Nm  "), "Custom");

    gDesc.putObject(charIDToTypeID("Grad"), charIDToTypeID("Grdn"), gColorDesc);
    gDesc.putUnitDouble(charIDToTypeID("Angl"), charIDToTypeID("#Ang"), {angle});
    gDesc.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("GrdT"), charIDToTypeID("Lnr "));
    gDesc.putBoolean(charIDToTypeID("Rvrs"), false);
    gDesc.putBoolean(charIDToTypeID("Algn"), true);
    gDesc.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), 100);

    executeAction(charIDToTypeID("FlCn"), gDesc, DialogModes.NO);
    doc.selection.deselect();
    lyr.name;
    """
    _eval(jsx)
    return {"status": "gradient_added", "layer": layer_name}


# ---------------------------------------------------------------------------
# Gradient overlay (dark-to-transparent, for text legibility)
# ---------------------------------------------------------------------------

def add_gradient_overlay(
    height: int = 600,
    opacity: int = 60,
    layer_name: str = "Overlay degradado",
    from_bottom: bool = False,
) -> dict:
    """
    Add a black-to-transparent gradient layer over the top (or bottom) of the canvas.
    Uses PS opacity stops so the gradient truly fades to transparent — no solid block.
    opacity: overall layer opacity (0-100). Keep subtle: 50-70.
    from_bottom: if True, gradient goes dark at bottom fading upward.
    """
    name_escaped = _jsx_string(layer_name)
    angle = 270 if from_bottom else 90
    # Compute selection coords in Python to avoid f-string conditional issues
    y0_expr = f"canvasH - {height}" if from_bottom else "0"
    y1_expr = "canvasH" if from_bottom else str(height)
    jsx = f"""
    app.displayDialogs = DialogModes.NO;
    var doc = app.activeDocument;
    var canvasW = doc.width.as('px');
    var canvasH = doc.height.as('px');

    var lyr = doc.artLayers.add();
    lyr.name = "{name_escaped}";

    var y0 = {y0_expr};
    var y1 = {y1_expr};
    var region = [[0,y0],[canvasW,y0],[canvasW,y1],[0,y1]];
    doc.selection.select(region);

    // Build gradient: black with opacity stops 100%→0%
    var gradDef = new ActionDescriptor();
    gradDef.putEnumerated(charIDToTypeID("GrdT"), charIDToTypeID("GrdT"), charIDToTypeID("CStr"));
    gradDef.putString(charIDToTypeID("Nm  "), "DarkFade");

    var stopList = new ActionList();
    var cs = new ActionDescriptor();
    var col = new ActionDescriptor();
    col.putDouble(charIDToTypeID("Rd  "), 0);
    col.putDouble(charIDToTypeID("Grn "), 0);
    col.putDouble(charIDToTypeID("Bl  "), 0);
    cs.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), col);
    cs.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("Clry"), charIDToTypeID("UsrS"));
    cs.putInteger(charIDToTypeID("Lctn"), 0);
    cs.putInteger(charIDToTypeID("Mdpn"), 50);
    stopList.putObject(charIDToTypeID("Clrt"), cs);
    gradDef.putList(charIDToTypeID("Clrs"), stopList);

    var transList = new ActionList();
    var t1 = new ActionDescriptor();
    t1.putInteger(charIDToTypeID("Opct"), 100);
    t1.putInteger(charIDToTypeID("Lctn"), 0);
    t1.putInteger(charIDToTypeID("Mdpn"), 50);
    transList.putObject(charIDToTypeID("TrnS"), t1);
    var t2 = new ActionDescriptor();
    t2.putInteger(charIDToTypeID("Opct"), 0);
    t2.putInteger(charIDToTypeID("Lctn"), 4096);
    t2.putInteger(charIDToTypeID("Mdpn"), 50);
    transList.putObject(charIDToTypeID("TrnS"), t2);
    gradDef.putList(charIDToTypeID("Trns"), transList);

    var gDesc = new ActionDescriptor();
    gDesc.putObject(charIDToTypeID("Grad"), charIDToTypeID("Grdn"), gradDef);
    gDesc.putUnitDouble(charIDToTypeID("Angl"), charIDToTypeID("#Ang"), {angle});
    gDesc.putEnumerated(charIDToTypeID("Type"), charIDToTypeID("GrdT"), charIDToTypeID("Lnr "));
    gDesc.putBoolean(charIDToTypeID("Rvrs"), false);
    gDesc.putBoolean(charIDToTypeID("Algn"), true);
    gDesc.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), 100);

    executeAction(charIDToTypeID("FlCn"), gDesc, DialogModes.NO);
    doc.selection.deselect();
    lyr.opacity = {opacity};
    lyr.name;
    """
    _eval(jsx)
    return {{"status": "gradient_overlay_added", "layer": layer_name, "height": height, "opacity": opacity}}


# ---------------------------------------------------------------------------
# Shapes
# ---------------------------------------------------------------------------

def add_rectangle(
    x: int,
    y: int,
    width: int,
    height: int,
    color_hex: str,
    layer_name: str = "Rectangle",
    opacity: int = 100,
) -> dict:
    """Add a filled rectangle on a new pixel layer."""
    r, g, b = _rgb(color_hex)
    name_escaped = _jsx_string(layer_name)
    x2, y2 = x + width, y + height
    jsx = f"""
    var doc = app.activeDocument;
    var lyr = doc.artLayers.add();
    lyr.name = "{name_escaped}";
    lyr.opacity = {opacity};
    var region = [[{x},{y}],[{x2},{y}],[{x2},{y2}],[{x},{y2}]];
    doc.selection.select(region);
    var c = new SolidColor();
    c.rgb.red = {r}; c.rgb.green = {g}; c.rgb.blue = {b};
    doc.selection.fill(c, ColorBlendMode.NORMAL, 100, false);
    doc.selection.deselect();
    lyr.name;
    """
    _eval(jsx)
    return {"status": "rectangle_added", "layer": layer_name}


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------

def add_text_layer(
    text: str,
    x: int,
    y: int,
    font_name: str,
    font_size: float,
    color_hex: str,
    layer_name: str = "",
    bold: bool = False,
    italic: bool = False,
    alignment: str = "LEFT",
    tracking: int = 0,
) -> dict:
    """Add a text layer with full typographic control."""
    r, g, b = _rgb(color_hex)
    layer_name = layer_name or f"Text_{text[:20].replace(' ', '_')}"
    name_escaped = _jsx_string(layer_name)
    text_escaped = _jsx_string(text)
    font_escaped = _jsx_string(font_name)
    alignment = alignment.upper()

    jsx = f"""
    var doc = app.activeDocument;
    var lyr = doc.artLayers.add();
    lyr.kind = LayerKind.TEXT;
    lyr.name = "{name_escaped}";

    var ti = lyr.textItem;
    ti.contents = "{text_escaped}";
    ti.position = new Array({x}, {y});
    ti.size = new UnitValue({font_size}, "pt");

    var c = new SolidColor();
    c.rgb.red = {r}; c.rgb.green = {g}; c.rgb.blue = {b};
    ti.color = c;

    try {{ ti.font = "{font_escaped}"; }} catch(e) {{ ti.font = "ArialMT"; }}

    ti.justification = Justification.{alignment};
    {"ti.fauxBold = true;" if bold else ""}
    {"ti.fauxItalic = true;" if italic else ""}
    {"ti.tracking = " + str(tracking) + ";" if tracking else ""}

    lyr.name;
    """
    _eval(jsx)
    return {"status": "text_added", "layer": layer_name, "text": text}


# ---------------------------------------------------------------------------
# Layer effects
# ---------------------------------------------------------------------------

def apply_drop_shadow(
    layer_name: str,
    color_hex: str = "#000000",
    opacity: int = 75,
    angle: int = 120,
    distance: int = 5,
    size: int = 10,
) -> dict:
    """Apply a drop shadow effect to the named layer."""
    r, g, b = _rgb(color_hex)
    name_escaped = _jsx_string(layer_name)
    jsx = f"""
    var doc = app.activeDocument;
    var target = null;
    for (var i = 0; i < doc.artLayers.length; i++) {{
        if (doc.artLayers[i].name === "{name_escaped}") {{
            target = doc.artLayers[i]; break;
        }}
    }}
    if (!target) {{ 'layer_not_found'; }} else {{
        doc.activeLayer = target;
        var desc  = new ActionDescriptor();
        var ref   = new ActionReference();
        ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
        desc.putReference(charIDToTypeID("null"), ref);

        var fx    = new ActionDescriptor();
        var shade = new ActionDescriptor();
        shade.putBoolean(charIDToTypeID("enab"), true);
        shade.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
        var sc = new ActionDescriptor();
        sc.putDouble(charIDToTypeID("Rd  "), {r});
        sc.putDouble(charIDToTypeID("Grn "), {g});
        sc.putDouble(charIDToTypeID("Bl  "), {b});
        shade.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), sc);
        shade.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), {opacity});
        shade.putBoolean(charIDToTypeID("uglg"), true);
        shade.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), {angle});
        shade.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), {distance});
        shade.putUnitDouble(charIDToTypeID("Ckmt"), charIDToTypeID("#Pxl"), 0);
        shade.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), {size});
        shade.putUnitDouble(charIDToTypeID("Nose"), charIDToTypeID("#Prc"), 0);
        fx.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), shade);
        desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), fx);
        executeAction(charIDToTypeID("setd"), desc, DialogModes.NO);
        target.name;
    }}
    """
    _eval(jsx)
    return {"status": "shadow_applied", "layer": layer_name}


# ---------------------------------------------------------------------------
# Image placement
# ---------------------------------------------------------------------------

def place_image_as_background(file_path: str, layer_name: str = "Foto fondo") -> dict:
    """Place a JPG/PNG as a Smart Object scaled to fill the canvas (cover mode)."""
    file_path = file_path.replace("\\", "/")
    name_escaped = _jsx_string(layer_name)
    jsx = f"""
    app.displayDialogs = DialogModes.NO;
    var doc = app.activeDocument;
    var canvasW = doc.width.as('px');
    var canvasH = doc.height.as('px');

    // Place as Smart Object (File > Place)
    var placeDesc = new ActionDescriptor();
    placeDesc.putPath(charIDToTypeID("null"), new File("{_jsx_string(file_path)}"));
    placeDesc.putEnumerated(charIDToTypeID("FTcs"), charIDToTypeID("QCSt"), charIDToTypeID("Qcsa"));
    executeAction(charIDToTypeID("Plc "), placeDesc, DialogModes.NO);

    var lyr = doc.activeLayer;
    lyr.name = "{name_escaped}";

    // Scale to cover canvas (cover mode)
    var bounds = lyr.bounds;
    var imgW = bounds[2].as('px') - bounds[0].as('px');
    var imgH = bounds[3].as('px') - bounds[1].as('px');
    var scaleX = (canvasW / imgW) * 100;
    var scaleY = (canvasH / imgH) * 100;
    var scale = Math.max(scaleX, scaleY);
    lyr.resize(scale, scale, AnchorPosition.MIDDLECENTER);

    // Center on canvas
    var nb = lyr.bounds;
    var lyrW = nb[2].as('px') - nb[0].as('px');
    var lyrH = nb[3].as('px') - nb[1].as('px');
    var deltaX = (canvasW - lyrW) / 2 - nb[0].as('px');
    var deltaY = (canvasH - lyrH) / 2 - nb[1].as('px');
    lyr.translate(deltaX, deltaY);

    lyr.moveToEnd();
    lyr.name;
    """
    _eval(jsx)
    return {"status": "background_placed_smart_object", "layer": layer_name, "file": file_path}


def place_image_at(
    file_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
    layer_name: str = "Image",
) -> dict:
    """Place a JPG/PNG as a smart object at a specific position and size."""
    file_path = file_path.replace("\\", "/")
    name_escaped = _jsx_string(layer_name)
    jsx = f"""
    var doc = app.activeDocument;

    var placeDesc = new ActionDescriptor();
    placeDesc.putPath(charIDToTypeID("null"), new File("{_jsx_string(file_path)}"));
    placeDesc.putEnumerated(charIDToTypeID("FTcs"), charIDToTypeID("QCSt"), charIDToTypeID("Qcsa"));
    executeAction(charIDToTypeID("Plc "), placeDesc, DialogModes.NO);

    var lyr = doc.activeLayer;
    lyr.name = "{name_escaped}";

    // Get current size
    var bounds = lyr.bounds;
    var imgW = bounds[2].as('px') - bounds[0].as('px');
    var imgH = bounds[3].as('px') - bounds[1].as('px');

    // Scale to target size
    var scaleX = ({width} / imgW) * 100;
    var scaleY = ({height} / imgH) * 100;
    lyr.resize(scaleX, scaleY, AnchorPosition.TOPLEFT);

    // Move to target position
    var nb = lyr.bounds;
    lyr.translate({x} - nb[0].as('px'), {y} - nb[1].as('px'));

    lyr.name;
    """
    _eval(jsx)
    return {"status": "image_placed", "layer": layer_name, "x": x, "y": y, "width": width, "height": height}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_as_png(output_path: str) -> dict:
    """Export the active document as PNG (Save for Web)."""
    output_path = output_path.replace("\\", "/")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    jsx = f"""
    var doc = app.activeDocument;
    var opts = new ExportOptionsSaveForWeb();
    opts.format = SaveDocumentType.PNG;
    opts.PNG8 = false;
    opts.quality = 100;
    doc.exportDocument(new File("{output_path}"), ExportType.SAVEFORWEB, opts);
    'exported';
    """
    _eval(jsx)
    return {"status": "exported_png", "output": output_path}


def export_as_jpg(output_path: str, quality: int = 90) -> dict:
    """Flatten and export the active document as JPEG."""
    output_path = output_path.replace("\\", "/")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    # Photoshop quality scale is 0-12; map 0-100 → 0-12
    ps_quality = round(quality / 100 * 12)
    jsx = f"""
    var dup = app.activeDocument.duplicate();
    dup.flatten();
    var jOpts = new JPEGSaveOptions();
    jOpts.quality = {ps_quality};
    dup.saveAs(new File("{output_path}"), jOpts, true);
    dup.close(SaveOptions.DONOTSAVECHANGES);
    'exported';
    """
    _eval(jsx)
    return {"status": "exported_jpg", "output": output_path}
