"""Generate La Linda background image via Flow — no Anthropic API needed."""
import sys
sys.path.insert(0, r"C:\Users\Estudio Creador\Desktop\Claudecodetest")

from tools.chrome_controller import generate_image_flow

prompt = (
    "Aerial drone view of a modern residential eco-neighborhood in Argentina, "
    "green open lots with paved streets and sidewalks, young Latin American family "
    "with two children walking happily together on a sunny afternoon, surrounded by "
    "tall trees and natural vegetation, wide open blue sky, warm golden hour lighting, "
    "elegant and peaceful suburban atmosphere, blue-grey and green color tones"
)

style_suffix = "cinematic photography, 8k, warm natural light, photorealistic, Canon 5D aerial"

result = generate_image_flow(
    prompt=prompt,
    output_path=r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\la_linda_familia_bg.png",
    style_suffix=style_suffix,
    wait_seconds=90,
)

print(result)
