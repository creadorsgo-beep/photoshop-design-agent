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
    return _app().eval_(jsx.strip())


# ---------------------------------------------------------------------------
# Document operations
# ---------------------------------------------------------------------------

def create_document(name: str, width: int, height: int, resolution: int = 72) -> dict:
    """Create a new RGB Photoshop document."""
    app = _app()
    app.documents.add(width, height, resolution, name)
    return {"status": "created", "name": name, "width": width, "height": height}


def open_template(file_path: str) -> dict:
    """Open an existing PSD file in Photoshop."""
    app = _app()
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
