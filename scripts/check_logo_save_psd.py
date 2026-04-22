import comtypes.client, os, sys

app = comtypes.client.CreateObject('Photoshop.Application')
doc = None
for i in range(app.documents.count):
    if app.documents[i].name == "habitar-historia-futuro":
        doc = app.documents[i]
        break

app.activeDocument = doc

jsx_check = """
var doc = app.activeDocument;
var result = "";
for (var i = 0; i < doc.layers.length; i++) {
    var ly = doc.layers[i];
    if (ly.name == "logo-grupo-habitar") {
        var b = ly.bounds;
        result = "Logo: " + Math.round(b[0]) + "," + Math.round(b[1]) + " -> " + Math.round(b[2]) + "," + Math.round(b[3]);
    }
}
result || "Logo NOT found";
"""
print(app.DoJavaScript(jsx_check))

# Save PSD
psd_path = os.path.abspath(os.path.join("output", "habitar-historia-futuro.psd"))
psd_path_fwd = psd_path.replace("\\", "/")
jsx_save = 'var psdFile = new File("' + psd_path_fwd + '"); var psdOpts = new PhotoshopSaveOptions(); psdOpts.embedColorProfile = true; psdOpts.layers = true; app.activeDocument.saveAs(psdFile, psdOpts, true, Extension.LOWERCASE); "PSD_SAVED";'
print(app.DoJavaScript(jsx_save))
