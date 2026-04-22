import comtypes.client, os, time

app = comtypes.client.CreateObject('Photoshop.Application')
doc = None
for i in range(app.documents.count):
    if app.documents[i].name == "habitar-historia-futuro":
        doc = app.documents[i]
        break

app.activeDocument = doc

# Reposition logo to bottom center
jsx = """
var doc = app.activeDocument;
for (var i = 0; i < doc.layers.length; i++) {
    if (doc.layers[i].name == "logo-grupo-habitar") {
        var ly = doc.layers[i];
        var b = ly.bounds;
        var layerW = b[2] - b[0];
        var layerH = b[3] - b[1];
        // Center X = 540, center Y = 1760
        var targetLeft = (1080 - layerW) / 2;
        var targetTop  = 1760 - layerH / 2;
        var dx = targetLeft - b[0];
        var dy = targetTop  - b[1];
        ly.translate(dx, dy);
        var nb = ly.bounds;
        "Moved to: " + Math.round(nb[0]) + "," + Math.round(nb[1]) + " size:" + Math.round(layerW) + "x" + Math.round(layerH);
        break;
    }
}
"""
print(app.DoJavaScript(jsx))

# Re-export PNG
output_png = os.path.abspath(os.path.join("output", "habitar-historia-futuro.png"))
output_png_fwd = output_png.replace("\\", "/")
jsx_png = (
    'var pngFile = new File("' + output_png_fwd + '");'
    'var pngOpts = new ExportOptionsSaveForWeb();'
    'pngOpts.format = SaveDocumentType.PNG;'
    'pngOpts.PNG8 = false;'
    'pngOpts.quality = 100;'
    'app.activeDocument.exportDocument(pngFile, ExportType.SAVEFORWEB, pngOpts);'
    '"PNG_OK";'
)
print(app.DoJavaScript(jsx_png))

# Re-export JPG
output_jpg = os.path.abspath(os.path.join("output", "habitar-historia-futuro.jpg"))
output_jpg_fwd = output_jpg.replace("\\", "/")
jsx_jpg = (
    'var jpgFile = new File("' + output_jpg_fwd + '");'
    'var jpgOpts = new JPEGSaveOptions();'
    'jpgOpts.quality = 10;'
    'var flat = app.activeDocument.duplicate();'
    'flat.flatten();'
    'flat.saveAs(jpgFile, jpgOpts, true, Extension.LOWERCASE);'
    'flat.close(SaveOptions.DONOTSAVECHANGES);'
    '"JPG_OK";'
)
print(app.DoJavaScript(jsx_jpg))
print("DONE")
