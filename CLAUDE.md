# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**Photoshop Design Agent** — a Python AI agent that reads content plans from Google Drive, analyzes existing PSD files for brand style (colors, typography, composition), and creates professional designs directly in Adobe Photoshop using the Claude API.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, DRIVE_FOLDER_ID, and Google credential paths
```

Google Drive credentials require a one-time OAuth flow:
1. Google Cloud Console → create project → enable **Drive API** + **Docs API**
2. Credentials → OAuth 2.0 Client ID (Desktop app) → download JSON → save as `credentials/credentials.json`
3. First run opens a browser for authorization, then saves `credentials/token.json`

Photoshop must be installed locally (Windows). The agent opens it automatically via COM.

## Running the agent

```bash
# Interactive mode
python main.py

# Analyze a folder of PSDs and save style guide for a client
python main.py --analyze-folder "C:/Designs/PalauHistorias" --save-client "palau historias"

# Create a design using a saved client style
python main.py "Create a 1080x1080 Instagram post" --load-client "palau historias"

# With a reference PSD
python main.py --doc-id 1BxiMxxxxxxx --reference-psd "C:/Designs/brand.psd"
python main.py "Create banner" --reference-psd refs/style.psd --quiet
```

## Architecture

```
main.py              CLI entry point — builds the request and calls run_agent()
agent.py             Agent loop: Claude API + tool dispatcher + streaming
tools/
  psd_analyzer.py   Parses PSD files offline (psd-tools, no Photoshop needed)
                     → returns color_palette, fonts, text_elements, design_patterns
  ps_executor.py     Controls Photoshop via COM + ExtendScript (JSX) eval
                     → create_document, add_text_layer, add_rectangle, export_as_png …
  drive_reader.py    Google Drive/Docs API — list_files(), read_document()
credentials/         OAuth token + credentials.json (git-ignored)
output/              Exported PNG/JPG/PSD files land here
```

### Agent design

The agent uses `claude-opus-4-7` with adaptive thinking and a manual tool-use loop. It streams each response and stops when `stop_reason == "end_turn"`. All Photoshop operations go through `ps_executor.py` which calls `app.eval_(jsx)` on the Photoshop COM object.

### Photoshop executor (ps_executor.py)

Every function calls `ps.Application()` (connects to or opens PS), then runs JSX via `app.eval_()`. Key functions:

| Function | What it does |
|---|---|
| `create_document(name, w, h, res)` | New blank canvas |
| `set_background_color(hex)` | Fill background layer |
| `add_gradient_background(c1, c2, angle)` | Linear gradient fill layer |
| `add_rectangle(x, y, w, h, hex)` | Filled pixel rectangle |
| `add_text_layer(text, x, y, font, size, hex, ...)` | Text layer with full styling |
| `apply_drop_shadow(layer_name, ...)` | Drop shadow via PS action manager |
| `export_as_png(path)` | Save for Web → PNG |
| `export_as_jpg(path, quality)` | Flatten + JPEG save |
| `save_as_psd(path)` | Layered PSD copy |

**Text positioning**: `(x, y)` is the baseline of the first line. To visually place text starting at pixel `top_y`, set `y = top_y + font_size`.

**Font names** must be PostScript names (e.g. `ArialMT`, `HelveticaNeue-Bold`, `MyriadPro-Regular`). If a font is missing, the executor falls back to `ArialMT`.

### PSD analyzer (psd_analyzer.py)

Uses `psd-tools` to parse the binary PSD without opening Photoshop. Returns:
- `canvas` — width, height
- `color_palette` — hex list (from text colors + dominant colors via PIL quantize)
- `fonts` — list of `{name, style, sizes[], tracking}`
- `text_elements` — each text layer: content, bounds, font, size, color
- `design_patterns` — primary_color, typography_hierarchy (heading/subheading/body sizes)

Engine data parsing extracts font name, size, tracking, and fill color from the `StyleRun.RunArray` in Photoshop's text engine format.

## Adding new Photoshop operations

Add a Python function in `tools/ps_executor.py` that builds a JSX string and calls `_eval(jsx)`. Then:
1. Add a tool schema entry in the `TOOLS` list in `agent.py`
2. Add a dispatch case in `_execute_tool()` in `agent.py`

When writing JSX: use `_jsx_string(text)` to safely escape any user text that goes into JSX string literals. All hex colors convert via `_rgb(hex)` → `(r, g, b)` tuple.

## Base de conocimiento de diseño

Los siguientes archivos contienen el conocimiento técnico y conceptual de diseño que debe aplicarse en todo momento al trabajar con este agente. Son la referencia para decisiones de composición, tipografía, color, especificaciones de plataforma y workflows de Adobe.

@knowledge/01-especificaciones-tecnicas.md
@knowledge/02-composicion-visual.md
@knowledge/03-tipografia.md
@knowledge/04-color.md
@knowledge/05-adobe-workflows.md
@knowledge/06-formatos-exportacion.md
@knowledge/07-sistemas-design.md
