"""
Photoshop Design Agent — orchestrates Claude + tools to create PS designs.

Flow:
  1. Claude reads the content plan (Google Drive)
  2. Claude analyzes reference PSD files (style extraction)
  3. Claude creates the design step-by-step in Photoshop
  4. Claude exports the final files

Usage:
  from agent import run_agent
  result = run_agent("Create a 1080x1080 Instagram post for...")
"""

import json
import os
from dotenv import load_dotenv
load_dotenv()
import anthropic
from tools.psd_analyzer import analyze_psd, analyze_folder
from tools.style_memory import save_client_style, load_client_style, list_clients
from tools.ps_executor import (
    create_document,
    open_template,
    get_document_info,
    save_as_psd,
    set_background_color,
    add_gradient_background,
    add_gradient_overlay,
    add_rectangle,
    add_text_layer,
    apply_drop_shadow,
    export_as_png,
    export_as_jpg,
    place_image_as_background,
    place_image_at,
)
from tools.drive_reader import list_files, read_document
from tools.chrome_controller import generate_image_flow, take_flow_screenshot, explore_flow_ui

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"
MAX_HISTORY_MESSAGES = 20  # first user msg + last N-1 to cap context growth

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a professional graphic designer AI agent that creates Photoshop designs.

You have access to tools for:
  • Reading content plans from Google Drive
  • Analyzing existing PSD files to extract brand style (colors, fonts, layout, composition)
  • Creating designs in Adobe Photoshop step by step
  • Generating photos and illustrations via Google Labs Flow (Chrome automation)

## Client style guide workflow

When asked to analyze designs for a client:
1. Use `analyze_design_folder` on the folder containing their PSD files
2. Review the aggregated color_palette, fonts, canvas_sizes, and design_patterns
3. Synthesize a clean style guide dict — include your own observations about the
   visual language (minimal? bold? corporate? playful?)
4. Call `save_client_style` with the client name and the synthesized guide
5. Confirm what was found and saved (colors, fonts, typical dimensions)

When asked to create a design for a known client:
1. Call `load_client_style` first to retrieve their saved guide
2. Then follow the design process below using those exact colors and fonts

## Design process

1. **Understand the brief** — Read the content plan from Drive if provided. Note text content,
   purpose, dimensions (e.g. 1080×1080 for Instagram, 1920×1080 for banners).

2. **Extract the brand style** — If a reference PSD is provided, analyze it first. Extract:
   - Color palette (primary, secondary, accent, background, text colors)
   - Typography (font families, sizes hierarchy: heading / subheading / body, tracking)
   - Layout patterns (margins, alignment, element positioning)

3. **Plan the composition** — Decide the layer order (background → shapes → images → text),
   visual hierarchy, and element placement before creating anything.

4. **Build the design** — Execute step by step in Photoshop:
   a. create_new_design (or open_psd_template for existing base)
   b. set_background_color or add_gradient
   c. place_image_as_background or place_image_at for all images — these create Smart Objects (editable, non-destructive)
   d. add_rectangle for decorative blocks, panels, bars
   e. add_text (headlines first, then body, then fine print)
   f. apply_drop_shadow on text or elements for depth
   g. save_design_psd — ALWAYS save as PSD at the end (layered, editable). Do NOT export PNG.

5. **Report** — Confirm the PSD output path and summarize what was created.

## Smart Objects rule
ALL images (photos, logos, textures, generated images) must be placed via `place_image_as_background` or `place_image_at` — both use the Photoshop Place command which creates a Smart Object layer. NEVER flatten, rasterize, or paste pixels. The final file must be a fully editable layered PSD.

## Design principles

### Canvas & safe zones
- For 1080×1080 feed: safe zone x=54–1026, y=54–1026 (5% margin)
- For 1080×1350 feed 4:5: safe zone y=135–1215
- For 1080×1920 Stories: MANDATORY safe zone x=65–1015, y=250–1670. Photo/image full-bleed OK, but ALL text, logos and key elements must stay inside this zone.
  - y=250–450: header/logo zone
  - y=450–1100: golden zone (main content)
  - y=1100–1490: secondary content
  - y=1490–1670: CTA zone
- For TikTok: safe zone — avoid top 130px, bottom 380px, right 130px
- For LinkedIn 1200×627: margins 60px all sides

### Typography hierarchy (3 levels)
- Level 1 HERO: 67–110px, Bold/ExtraBold, 1 element — stops the scroll
- Level 2 SUPPORT: 21–37px, Regular/Medium, 1–2 lines
- Level 3 DETAIL: 10–16px, Regular, captions/disclaimers
- Text Y position: add font_size to Y for the visual top (baseline offset)
- Tracking for headlines: -10 to -20 units (slightly compressed)
- Tracking for uppercase tags/labels: +100 to +200 units

### Color
- Always work in RGB, sRGB color space
- Match the client palette exactly (hex values from style guide)
- Contrast rule: light text on dark BG, dark text on light BG (WCAG AA: 4.5:1 ratio)
- Structure: 60% primary / 30% secondary / 10% accent

### Composition
- Maximum 3 hierarchy levels per piece — if everything shouts, nothing does
- Rule of thirds for 1080×1920: power points at (360,640), (720,640), (360,1280), (720,1280)
- 1 message per piece — test: can someone understand it in 3 seconds?
- Premium brands use 30–50% negative space — resist filling every pixel
- Diagonal lines = dynamism; horizontal = calm; vertical = aspiration

### Layer structure (follow this order, bottom to top)
```
Background (color / gradient)
Photo/texture (Smart Object)
Color adjustments (non-destructive)
Decorative shapes / panels
Subject / product cutout (Smart Object)
Text elements (headline → subtitle → body)
Logo / brand mark (Smart Object)
```

### Components
- **Pill/tag**: rectangle with padding 16px H / 12px V, border-radius simulated via rounded rect, text SemiBold
- **Badge "new"**: small pill or circle, rotated ±15° for dynamism, max 3 words
- **Overlay for legibility**: gradient black→transparent (opacity 50–70%), NEVER solid rectangle
- **Drop shadow on text**: distance 0, size 8–15px, opacity 60–80%

### Non-destructive workflow (ALWAYS)
- All images → Smart Objects via place_image_as_background or place_image_at
- Adjustment layers for color corrections (never flatten)
- Save as layered PSD — do NOT flatten, do NOT export PNG as final deliverable

## Image generation with Google Labs Flow

When a design needs a photo, texture, or illustration:
1. Call `generate_image` with a carefully crafted prompt
2. Once you have the path, use `place_image_as_background` or `place_image_at`
3. Continue building the design on top

### How to write great Flow prompts

Structure: **[Subject] + [Setting/Context] + [Lighting] + [Mood/Atmosphere] + [Style] + [Technical]**

Examples by use case:
- Food/café: "freshly brewed espresso in a ceramic cup, golden hour light from window, warm amber tones, steam rising, shallow depth of field, photorealistic, Canon 5D"
- Architecture/place: "colonial stone archway in Latin America, late afternoon sun, vines growing on walls, cinematic wide shot, warm terracotta palette, 8k"
- Abstract/texture: "warm terracotta and cream linen texture, minimal, flat, close-up macro shot, soft natural light"
- People: "young professional woman smiling in a modern café, candid, natural window light, shallow DOF, authentic, photorealistic"

Always match the image tone to the brand color palette from the client style guide.
If Chrome/Flow is unavailable, use `inspect_flow` to diagnose the connection.

Always save as PSD and export as PNG when finished."""

# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "analyze_reference_psd",
        "description": (
            "Analyze an existing Photoshop PSD file to extract the design style "
            "including colors, typography, layout, and composition. Call this before "
            "creating a new design when a reference file is available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the PSD file to analyze",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_design_folder",
        "description": (
            "Analyze ALL PSD files inside a folder and aggregate them into a unified "
            "brand style guide: color palette (ranked by frequency), fonts (ranked by usage), "
            "canvas sizes, and typography hierarchy. Use this when building a client style guide "
            "from multiple reference designs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Absolute path to the folder containing PSD files",
                }
            },
            "required": ["folder_path"],
        },
    },
    {
        "name": "save_client_style",
        "description": (
            "Save a style guide dict under a client name for future use. "
            "The guide is stored as JSON in the clients/ directory and can be loaded "
            "later when creating new designs for the same client."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "Client name (e.g. 'palau historias')",
                },
                "style_guide": {
                    "type": "object",
                    "description": (
                        "Style guide dict to save. Should include: "
                        "color_palette (list of hex), fonts (list), "
                        "design_patterns (primary_color, typography_hierarchy, dominant_font), "
                        "canvas_sizes, and any design notes."
                    ),
                },
            },
            "required": ["client_name", "style_guide"],
        },
    },
    {
        "name": "load_client_style",
        "description": (
            "Load the previously saved style guide for a client. "
            "Use this at the start of any design session for a known client."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "Client name to load (e.g. 'palau historias')",
                }
            },
            "required": ["client_name"],
        },
    },
    {
        "name": "list_clients",
        "description": "List all clients that have saved style guides.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_drive_files",
        "description": "List files in a Google Drive folder to find content plans or reference documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_id": {
                    "type": "string",
                    "description": "Drive folder ID (leave empty for default from config)",
                },
                "file_type": {
                    "type": "string",
                    "enum": ["all", "docs", "sheets"],
                    "description": "Filter by file type",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_google_doc",
        "description": "Read the full text content of a Google Document. Use to read content plans, briefs, and copy text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Google Document ID (from the URL)",
                }
            },
            "required": ["doc_id"],
        },
    },
    {
        "name": "create_new_design",
        "description": "Create a new blank Photoshop document. Call this once at the start of a new design.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Document name"},
                "width": {"type": "integer", "description": "Width in pixels"},
                "height": {"type": "integer", "description": "Height in pixels"},
                "resolution": {
                    "type": "integer",
                    "description": "DPI — 72 for screen/social, 300 for print",
                },
            },
            "required": ["name", "width", "height"],
        },
    },
    {
        "name": "open_psd_template",
        "description": "Open an existing PSD file in Photoshop as the base for a new design.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the PSD template file",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "get_document_info",
        "description": "Get canvas dimensions and layer list of the currently active Photoshop document.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "set_background_color",
        "description": "Fill the canvas background with a solid color.",
        "input_schema": {
            "type": "object",
            "properties": {
                "color_hex": {
                    "type": "string",
                    "description": "Background color as hex (e.g. '#1a2b3c')",
                }
            },
            "required": ["color_hex"],
        },
    },
    {
        "name": "add_gradient",
        "description": "Add a linear gradient fill layer spanning the full canvas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "color1_hex": {"type": "string", "description": "Start color hex"},
                "color2_hex": {"type": "string", "description": "End color hex"},
                "angle": {
                    "type": "integer",
                    "description": "Gradient angle: 0=horizontal, 90=top-to-bottom, 135=diagonal",
                },
                "layer_name": {"type": "string", "description": "Layer name"},
            },
            "required": ["color1_hex", "color2_hex"],
        },
    },
    {
        "name": "add_rectangle",
        "description": "Add a filled rectangle pixel layer. Use for backgrounds, panels, decorative bars, and color blocks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Left edge in pixels"},
                "y": {"type": "integer", "description": "Top edge in pixels"},
                "width": {"type": "integer", "description": "Width in pixels"},
                "height": {"type": "integer", "description": "Height in pixels"},
                "color_hex": {"type": "string", "description": "Fill color hex"},
                "layer_name": {"type": "string", "description": "Layer name"},
                "opacity": {"type": "integer", "description": "Opacity 0–100"},
            },
            "required": ["x", "y", "width", "height", "color_hex"],
        },
    },
    {
        "name": "add_text",
        "description": (
            "Add a text layer to the design. "
            "Position (x, y) sets the text baseline: if font_size is 48pt, "
            "set y = desired_visual_top + 48 to align the top of the text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text content"},
                "x": {"type": "integer", "description": "Horizontal position (left edge of text)"},
                "y": {"type": "integer", "description": "Baseline Y position"},
                "font_name": {
                    "type": "string",
                    "description": "Font PostScript name (e.g. 'ArialMT', 'HelveticaNeue-Bold', 'MyriadPro-Regular')",
                },
                "font_size": {"type": "number", "description": "Font size in points"},
                "color_hex": {"type": "string", "description": "Text color hex"},
                "layer_name": {"type": "string", "description": "Optional layer name"},
                "bold": {"type": "boolean", "description": "Faux bold"},
                "italic": {"type": "boolean", "description": "Faux italic"},
                "alignment": {
                    "type": "string",
                    "enum": ["LEFT", "CENTER", "RIGHT"],
                    "description": "Text justification",
                },
                "tracking": {
                    "type": "integer",
                    "description": "Letter spacing in thousandths of an em (0=normal, 100=wide)",
                },
            },
            "required": ["text", "x", "y", "font_name", "font_size", "color_hex"],
        },
    },
    {
        "name": "apply_drop_shadow",
        "description": "Apply a drop shadow layer style to a named layer for depth.",
        "input_schema": {
            "type": "object",
            "properties": {
                "layer_name": {"type": "string", "description": "Exact name of the layer"},
                "color_hex": {"type": "string", "description": "Shadow color hex (default #000000)"},
                "opacity": {"type": "integer", "description": "Shadow opacity 0–100"},
                "angle": {"type": "integer", "description": "Light angle in degrees"},
                "distance": {"type": "integer", "description": "Shadow offset in pixels"},
                "size": {"type": "integer", "description": "Feather/blur size in pixels"},
            },
            "required": ["layer_name"],
        },
    },
    {
        "name": "export_design_png",
        "description": "Export the active Photoshop document as a PNG file. Always call this at the end.",
        "input_schema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Full path including filename (e.g. 'output/design_final.png')",
                }
            },
            "required": ["output_path"],
        },
    },
    {
        "name": "export_design_jpg",
        "description": "Export the active document as a flattened JPEG.",
        "input_schema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Full path with filename"},
                "quality": {"type": "integer", "description": "JPEG quality 0–100"},
            },
            "required": ["output_path"],
        },
    },
    {
        "name": "save_design_psd",
        "description": "Save the active document as a layered PSD file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Full path with filename (e.g. 'output/design.psd')",
                }
            },
            "required": ["output_path"],
        },
    },
    {
        "name": "place_image_as_background",
        "description": "Place a JPG or PNG as a smart object background, scaled to fill the entire canvas (cover mode). Use this for photo backgrounds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path to the image file"},
                "layer_name": {"type": "string", "description": "Name for the layer"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "generate_image",
        "description": (
            "Generate a photo or illustration via Google Labs Flow (AI image generator) "
            "running in Chrome. Use this when the design needs a realistic photo, texture, "
            "background image, or any visual that doesn't exist as a file. "
            "Craft the prompt to match the brand style and design goal. "
            "Returns the path to the saved PNG, which you can then place_image_as_background or place_image_at."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Detailed image generation prompt. Be specific: subject, lighting, "
                        "mood, color palette, style (photorealistic, illustration, etc.), "
                        "composition. Example: 'A cozy Latin American coffee shop at golden hour, "
                        "warm amber light through wooden shutters, rustic stone walls, "
                        "espresso cups on marble counter, bokeh background, photorealistic'"
                    ),
                },
                "style_suffix": {
                    "type": "string",
                    "description": (
                        "Extra style keywords appended to the prompt, e.g. "
                        "'cinematic, 8k, photorealistic, shot on Canon 5D' or "
                        "'flat design, minimal, vector art'"
                    ),
                },
                "output_path": {
                    "type": "string",
                    "description": "Where to save the PNG. Auto-generated from prompt if empty.",
                },
                "wait_seconds": {
                    "type": "integer",
                    "description": "Max seconds to wait for generation (default 60)",
                },
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "inspect_flow",
        "description": (
            "Take a screenshot of Google Labs Flow in Chrome and return UI element info. "
            "Use this to diagnose issues or understand the current state of the browser."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "place_image_at",
        "description": "Place a JPG or PNG as a smart object at a specific position and size. Use this for logos and icons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path to the image file"},
                "x": {"type": "integer", "description": "Left edge in pixels"},
                "y": {"type": "integer", "description": "Top edge in pixels"},
                "width": {"type": "integer", "description": "Target width in pixels"},
                "height": {"type": "integer", "description": "Target height in pixels"},
                "layer_name": {"type": "string", "description": "Name for the layer"},
            },
            "required": ["file_path", "x", "y", "width", "height"],
        },
        "cache_control": {"type": "ephemeral"},
    },
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

def _execute_tool(name: str, tool_input: dict) -> str:
    try:
        if name == "analyze_reference_psd":
            result = analyze_psd(tool_input["file_path"])
            slim = {
                "canvas": result.get("canvas", {}),
                "color_palette": result.get("color_palette", [])[:8],
                "fonts": result.get("fonts", [])[:5],
                "design_patterns": result.get("design_patterns", {}),
                "text_elements": result.get("text_elements", [])[:6],
            }
            return json.dumps(slim)

        elif name == "analyze_design_folder":
            result = analyze_folder(tool_input["folder_path"])
            slim = {
                "canvas_sizes": result.get("canvas_sizes", []),
                "color_palette": result.get("color_palette", [])[:10],
                "fonts": result.get("fonts", [])[:6],
                "design_patterns": result.get("design_patterns", {}),
            }
            return json.dumps(slim)

        elif name == "save_client_style":
            result = save_client_style(
                tool_input["client_name"],
                tool_input["style_guide"],
            )
            return json.dumps(result)

        elif name == "load_client_style":
            result = load_client_style(tool_input["client_name"])
            return json.dumps(result, indent=2)

        elif name == "list_clients":
            result = list_clients()
            return json.dumps(result, indent=2)

        elif name == "list_drive_files":
            result = list_files(
                tool_input.get("folder_id") or None,
                tool_input.get("file_type", "all"),
            )
            return json.dumps(result, indent=2)

        elif name == "read_google_doc":
            return read_document(tool_input["doc_id"])

        elif name == "create_new_design":
            result = create_document(
                tool_input["name"],
                tool_input["width"],
                tool_input["height"],
                tool_input.get("resolution", 72),
            )
            return json.dumps(result)

        elif name == "open_psd_template":
            result = open_template(tool_input["file_path"])
            return json.dumps(result)

        elif name == "get_document_info":
            result = get_document_info()
            return json.dumps(result, indent=2)

        elif name == "set_background_color":
            result = set_background_color(tool_input["color_hex"])
            return json.dumps(result)

        elif name == "add_gradient":
            result = add_gradient_background(
                tool_input["color1_hex"],
                tool_input["color2_hex"],
                tool_input.get("angle", 90),
                tool_input.get("layer_name", "Gradient"),
            )
            return json.dumps(result)

        elif name == "add_rectangle":
            result = add_rectangle(
                tool_input["x"],
                tool_input["y"],
                tool_input["width"],
                tool_input["height"],
                tool_input["color_hex"],
                tool_input.get("layer_name", "Rectangle"),
                tool_input.get("opacity", 100),
            )
            return json.dumps(result)

        elif name == "add_text":
            result = add_text_layer(
                text=tool_input["text"],
                x=tool_input["x"],
                y=tool_input["y"],
                font_name=tool_input["font_name"],
                font_size=tool_input["font_size"],
                color_hex=tool_input["color_hex"],
                layer_name=tool_input.get("layer_name", ""),
                bold=tool_input.get("bold", False),
                italic=tool_input.get("italic", False),
                alignment=tool_input.get("alignment", "LEFT"),
                tracking=tool_input.get("tracking", 0),
            )
            return json.dumps(result)

        elif name == "apply_drop_shadow":
            result = apply_drop_shadow(
                layer_name=tool_input["layer_name"],
                color_hex=tool_input.get("color_hex", "#000000"),
                opacity=tool_input.get("opacity", 75),
                angle=tool_input.get("angle", 120),
                distance=tool_input.get("distance", 5),
                size=tool_input.get("size", 10),
            )
            return json.dumps(result)

        elif name == "place_image_as_background":
            result = place_image_as_background(
                tool_input["file_path"],
                tool_input.get("layer_name", "Foto fondo"),
            )
            return json.dumps(result)

        elif name == "place_image_at":
            result = place_image_at(
                tool_input["file_path"],
                tool_input["x"],
                tool_input["y"],
                tool_input["width"],
                tool_input["height"],
                tool_input.get("layer_name", "Image"),
            )
            return json.dumps(result)

        elif name == "export_design_png":
            result = export_as_png(tool_input["output_path"])
            return json.dumps(result)

        elif name == "export_design_jpg":
            result = export_as_jpg(
                tool_input["output_path"],
                tool_input.get("quality", 90),
            )
            return json.dumps(result)

        elif name == "save_design_psd":
            result = save_as_psd(tool_input["output_path"])
            return json.dumps(result)

        elif name == "generate_image":
            result = generate_image_flow(
                prompt=tool_input["prompt"],
                output_path=tool_input.get("output_path", ""),
                style_suffix=tool_input.get("style_suffix", ""),
                wait_seconds=tool_input.get("wait_seconds", 60),
            )
            return json.dumps(result)

        elif name == "inspect_flow":
            result = explore_flow_ui()
            return json.dumps(result, indent=2)

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as exc:
        return json.dumps({"error": str(exc), "tool": name})


# ---------------------------------------------------------------------------
# Main agent loop
# ---------------------------------------------------------------------------

def run_agent(user_request: str, verbose: bool = True) -> str:
    """
    Run the design agent for a given request.
    Returns the agent's final summary message.
    """
    messages = [{"role": "user", "content": user_request}]

    if verbose:
        print("\n" + "=" * 60)
        print("PHOTOSHOP DESIGN AGENT")
        print("=" * 60)
        print(f"Request: {user_request}\n")

    while True:
        if verbose:
            print("Thinking...")

        # Trim history to avoid unbounded context growth (keep first user msg + last N)
        if len(messages) > MAX_HISTORY_MESSAGES:
            messages = [messages[0]] + messages[-(MAX_HISTORY_MESSAGES - 1):]

        with client.messages.stream(
            model=MODEL,
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        # Print any text blocks
        for block in response.content:
            if block.type == "text" and verbose:
                print(f"\nAgent: {block.text}")

        if response.stop_reason == "end_turn":
            return next(
                (b.text for b in response.content if b.type == "text"),
                "Design completed.",
            )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"\n>> Tool: {block.name}")
                        input_preview = json.dumps(block.input, ensure_ascii=False)
                        if len(input_preview) > 300:
                            input_preview = input_preview[:300] + "..."
                        print(f"  Input: {input_preview}")

                    result = _execute_tool(block.name, block.input)

                    if verbose:
                        preview = result[:200] + "..." if len(result) > 200 else result
                        print(f"  Result: {preview}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Agent completed."
