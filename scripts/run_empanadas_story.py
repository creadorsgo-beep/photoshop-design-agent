# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run_agent

request = """
Diseña una Historia de Instagram (1080x1920) para el cliente Palau.

BRIEF:
- Titulo: "Proba lo nuevo"
- Subtitulo: "empanadas arabes"
- Agregar una pastillita/badge pequeña con el texto "new"
- Imagen: cutout del plato de empanadas sobre fondo verde marca

ASSETS:
- Cutout del plato: output/_emp01_cutout.png (PNG transparente)
- Logo: assets/palau-logo.png

PASOS:
1. load_client_style("palau")
2. create_new_design: nombre "palau-proba-lo-nuevo", 1080x1920, 72dpi
3. set_background_color #3d4725
4. place_image_at: file=output/_emp01_cutout.png, x=90, y=500, width=900, height=900, layer_name="Plato empanadas"
5. add_rectangle: x=65, y=250, width=900, height=105, color=#3d4725, layer_name="Pill titulo bg", opacity=0  (solo para referencia, no visible)
6. add_text: texto="Proba lo nuevo", x=540, y=365, font=AgenorNeue-SemiBold, size=110, color=#ffffff, alignment=CENTER, layer_name="Titulo"
7. add_rectangle: x=290, y=490, width=500, height=82, color=#2a3318, layer_name="Pill subtitulo"
8. add_text: texto="empanadas arabes", x=540, y=560, font=AgenorNeue-SemiBold, size=48, color=#ffffff, alignment=CENTER, layer_name="Subtitulo"
9. add_rectangle: x=820, y=510, width=140, height=52, color=#ffffff, layer_name="Badge new bg"
10. add_text: texto="new", x=890, y=553, font=AgenorNeue-SemiBold, size=32, color=#3d4725, alignment=CENTER, layer_name="Badge new text"
11. place_image_at: file=assets/palau-logo.png, x=430, y=1540, width=220, height=110, layer_name="Logo Palau"
12. save_design_psd: output/palau-proba-lo-nuevo.psd

REGLA CRITICA: Todas las imagenes van via place_image_at (Smart Objects). No exportar PNG. Guardar solo PSD.
Safe zone historia: x=65-1015, y=250-1670.
"""

run_agent(request, verbose=True)
