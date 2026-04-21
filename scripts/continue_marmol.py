"""Continue building marmol design - background already placed."""
import sys, time, os
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")
from dotenv import load_dotenv; load_dotenv()
from tools.ps_executor import add_text_layer, _eval

LOGO   = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\assets\palau-logo.png"
LOGO_JSX = LOGO.replace("\\", "/")
PSD_JSX = "C:/Users/Estudio Creador/Desktop/Claudecodetest/output/palau-marmol-v1.psd"

WHITE = "#FFFFFF"
GREEN = "#3d4725"
CREAM = "#F5F0E8"

def save():
    _eval(f'app.activeDocument.saveAs(new File("{PSD_JSX}"), new PhotoshopSaveOptions(), true);')
    time.sleep(1.5)
    print("   [saved]")

r = _eval("app.activeDocument.name;")
print("Active:", r)

# Bottom overlay (dark) for text legibility
print("1. Bottom overlay...")
_eval('var doc=app.activeDocument; var lyr=doc.artLayers.add(); lyr.name="OVERLAY/Bottom";')
_eval('var region=[[0,880],[1080,880],[1080,1920],[0,1920]]; app.activeDocument.selection.select(region);')
_eval('var c=new SolidColor(); c.rgb.hexValue="0d0d04"; app.activeDocument.selection.fill(c); app.activeDocument.selection.deselect();')
_eval('app.activeDocument.activeLayer.opacity=78;')
time.sleep(0.3)

# Top overlay (subtle) for logo area
print("2. Top overlay...")
_eval('var lyr=app.activeDocument.artLayers.add(); lyr.name="OVERLAY/Top";')
_eval('var region=[[0,0],[1080,0],[1080,370],[0,370]]; app.activeDocument.selection.select(region);')
_eval('var c=new SolidColor(); c.rgb.hexValue="0d0d04"; app.activeDocument.selection.fill(c); app.activeDocument.selection.deselect();')
_eval('app.activeDocument.activeLayer.opacity=55;')
time.sleep(0.3)

save()

# Logo
print("3. Logo...")
_eval(f'app.open(new File("{LOGO_JSX}"));')
time.sleep(0.5)
_eval("app.activeDocument.flatten(); app.activeDocument.selection.selectAll(); app.activeDocument.selection.copy();")
_eval("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
time.sleep(0.3)
_eval("app.activeDocument.paste();")
_eval('app.activeDocument.activeLayer.name="MARCA/Logo";')
_eval("""
var doc=app.activeDocument; doc.selection.deselect();
var lyr=doc.activeLayer;
var b=lyr.bounds;
var curH=b[3].as('px')-b[1].as('px');
var scale=(180/curH)*100;
lyr.resize(scale,scale,AnchorPosition.MIDDLECENTER);
b=lyr.bounds;
var cx=(b[0].as('px')+b[2].as('px'))/2;
var cy=(b[1].as('px')+b[3].as('px'))/2;
lyr.translate(540-cx, 305-cy);
lyr.moveToBeginning(doc);
""")
print("   Logo placed.")

# Green pill
print("4. Brand pill...")
_eval('var lyr=app.activeDocument.artLayers.add(); lyr.name="TEXTO/Pill";')
_eval('var r=[[108,1100],[395,1100],[395,1150],[108,1150]]; app.activeDocument.selection.select(r);')
_eval('var c=new SolidColor(); c.rgb.hexValue="3d4725"; app.activeDocument.selection.fill(c); app.activeDocument.selection.deselect();')
add_text_layer("NUEVO EN PALAU", x=124, y=1134, font_name="AgenorNeue-SemiBold", font_size=16, color_hex=WHITE, layer_name="TEXTO/PillText")
time.sleep(0.3)

# Title
print("5. Title (Jalliestha)...")
add_text_layer("Proba\nlo nuevo", x=108, y=1185, font_name="Jalliestha", font_size=118, color_hex=WHITE, layer_name="TEXTO/Titulo")
time.sleep(0.5)

# Subtitle
print("6. Subtitle...")
add_text_layer("Empanadas arabes", x=108, y=1435, font_name="AgenorNeue-SemiBold", font_size=40, color_hex=CREAM, layer_name="TEXTO/Subtitulo")
time.sleep(0.3)

# Description
print("7. Description...")
add_text_layer("Rellenas de carne, especias y pinones. Una receta con historia.", x=108, y=1500, font_name="AgenorNeue-SemiBold", font_size=24, color_hex="#AAAAAA", layer_name="TEXTO/Descripcion")
time.sleep(0.3)

# CTA
print("8. CTA...")
add_text_layer("Disponibles ahora", x=108, y=1720, font_name="AgenorNeue-SemiBold", font_size=30, color_hex=WHITE, layer_name="TEXTO/CTA")
_eval('var lyr=app.activeDocument.artLayers.add(); lyr.name="TEXTO/CTALine";')
_eval('var r=[[108,1760],[340,1760],[340,1764],[108,1764]]; app.activeDocument.selection.select(r);')
_eval('var c=new SolidColor(); c.rgb.hexValue="3d4725"; app.activeDocument.selection.fill(c); app.activeDocument.selection.deselect();')
time.sleep(0.3)

# Final save
print("\n9. Final save...")
save()
print("=== Done! output/palau-marmol-v1.psd ===")
