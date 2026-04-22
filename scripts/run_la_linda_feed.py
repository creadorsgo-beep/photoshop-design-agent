"""Run La Linda feed design via agent."""
import sys
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")

from agent import run_agent

request = (
    "Crea un feed de Instagram 1080x1350 para La Linda (sub-marca de Grupo Habitar).\n\n"
    "## Brief\n"
    "- Titulo: CRECE JUNTO A NUESTRO PROYECTO\n"
    "- Subtitulo: Santo Domingo, cerca de todo\n"
    "- Sub-marca: La Linda (colores: #435473 azul grisaceo, blanco #ffffff)\n"
    "- Logos: Logo La Linda arriba izquierda, Logo Grupo Habitar abajo centrado\n\n"
    "## Paso 1 — Cargar estilo del cliente\n"
    "Llama load_client_style con client_name='grupo habitar' para tener la paleta exacta.\n\n"
    "## Paso 2 — Generar imagen con Flow\n"
    "Genera una imagen AI con generate_image usando este prompt:\n"
    "'Aerial drone view of a modern residential eco-neighborhood in Argentina, "
    "green open lots with paved streets and sidewalks, young Latin American family "
    "with two children walking happily on a sunny afternoon, surrounded by trees "
    "and nature, wide open blue sky, warm golden hour lighting, elegant and peaceful "
    "atmosphere, blue-grey and green color palette, photorealistic, high detail'\n"
    "style_suffix: 'cinematic, 8k, warm natural light, eco neighborhood Argentina'\n"
    "output_path: 'C:/Users/Estudio Creador/Desktop/Claudecodetest/output/la_linda_familia_bg.png'\n\n"
    "## Paso 3 — Construir el diseno en Photoshop\n"
    "1. create_new_design: nombre='La Linda - Crece junto', width=1080, height=1350, resolution=72\n"
    "2. place_image_as_background: la imagen generada (la_linda_familia_bg.png), layer_name='Foto fondo'\n"
    "3. add_rectangle: overlay navy en zona de texto: x=0, y=680, width=1080, height=670, color_hex='#0d214b', opacity=60, layer_name='Overlay texto'\n"
    "4. add_rectangle: franja navy solida al pie: x=0, y=1230, width=1080, height=120, color_hex='#0d214b', opacity=100, layer_name='Franja pie'\n"
    "5. place_image_at: logo La Linda — file_path='//ASUSAGU/Freelance/grupo habitar/Logo-la-linda-Logo.png', x=54, y=60, width=210, height=84, layer_name='Logo La Linda'\n"
    "6. add_text: 'CRECE JUNTO A', font_name='GeometosSoft-ExtraBold', font_size=78, color_hex='#ffffff', x=54, y=840, alignment='LEFT', layer_name='Titulo L1'\n"
    "7. add_text: 'NUESTRO PROYECTO', font_name='GeometosSoft-ExtraBold', font_size=78, color_hex='#ffffff', x=54, y=930, alignment='LEFT', layer_name='Titulo L2'\n"
    "8. add_rectangle: linea separadora celeste: x=54, y=955, width=260, height=5, color_hex='#1993bc', layer_name='Linea acento'\n"
    "9. add_text: 'Santo Domingo, cerca de todo', font_name='GeometosSoft-Regular', font_size=38, color_hex='#ffffff', x=54, y=1040, alignment='LEFT', tracking=50, layer_name='Subtitulo'\n"
    "10. place_image_at: logo Grupo Habitar blanco — file_path='//ASUSAGU/Freelance/grupo habitar/blanco-Logo-grupo-habitar.png', x=390, y=1248, width=300, height=72, layer_name='Logo GH'\n"
    "11. apply_drop_shadow en layer_name='Titulo L1', opacity=70, distance=0, size=12\n"
    "12. apply_drop_shadow en layer_name='Titulo L2', opacity=70, distance=0, size=12\n"
    "13. apply_drop_shadow en layer_name='Subtitulo', opacity=60, distance=0, size=8\n"
    "14. save_design_psd: output_path='C:/Users/Estudio Creador/Desktop/Claudecodetest/output/la_linda_crece_junto.psd'\n"
)

run_agent(request, verbose=True)
