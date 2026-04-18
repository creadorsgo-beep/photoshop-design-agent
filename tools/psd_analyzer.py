"""
Analyzes PSD files to extract design style: colors, typography, layout, composition.
Uses psd-tools (no Photoshop required) to parse the binary PSD format.
"""

import os
from collections import Counter
from psd_tools import PSDImage
from psd_tools.constants import LayerKind
from PIL import Image


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _extract_dominant_colors(psd: PSDImage, max_colors: int = 12) -> list[str]:
    """Sample dominant colors from the flattened composite image."""
    try:
        composite = psd.topil()
        if not composite:
            return []
        if composite.mode != "RGB":
            composite = composite.convert("RGB")
        composite.thumbnail((200, 200))
        quantized = composite.quantize(colors=max_colors)
        palette = quantized.getpalette()
        colors = []
        for i in range(0, max_colors * 3, 3):
            r, g, b = palette[i], palette[i + 1], palette[i + 2]
            if r + g + b > 15:
                colors.append(_rgb_to_hex(r, g, b))
        return list(dict.fromkeys(colors))
    except Exception:
        return []


def _extract_text_styling(layer) -> dict:
    """Pull font, size, color, and spacing from a text layer's engine data."""
    styling = {}
    try:
        if not (hasattr(layer, "engine_data") and layer.engine_data):
            return styling
        ed = layer.engine_data
        run_array = (
            ed.get("EngineDict", {}).get("StyleRun", {}).get("RunArray", [])
        )
        for run in run_array:
            style_data = (
                run.get("StyleSheet", {}).get("StyleSheetData", {})
            )

            font_obj = style_data.get("Font", {})
            if isinstance(font_obj, dict):
                name = font_obj.get("Name", "")
                if name:
                    styling["font_name"] = name
                    styling["font_style"] = font_obj.get("StyleName", "")

            size = style_data.get("FontSize")
            if size:
                styling["font_size"] = round(float(size), 1)

            styling["tracking"] = style_data.get("Tracking", 0)
            styling["leading"] = style_data.get("Leading", 0)

            fill = style_data.get("FillColor", {}).get("Values", [])
            if len(fill) == 4:
                r, g, b = int(fill[1] * 255), int(fill[2] * 255), int(fill[3] * 255)
                styling["color"] = _rgb_to_hex(r, g, b)

            if styling:
                break
    except Exception:
        pass
    return styling


def _process_layer(layer, depth: int, state: dict) -> dict:
    """Recursively extract metadata from a single layer."""
    info = {
        "name": layer.name,
        "depth": depth,
        "visible": layer.visible,
        "opacity": layer.opacity,
        "bounds": {
            "left": layer.left,
            "top": layer.top,
            "width": layer.width,
            "height": layer.height,
        },
        "type": "GROUP" if layer.is_group() else "PIXEL",
    }

    if hasattr(layer, "kind"):
        info["type"] = layer.kind.name

    if hasattr(layer, "kind") and layer.kind == LayerKind.TYPE:
        info["type"] = "TEXT"
        try:
            info["text_content"] = layer.text
        except Exception:
            info["text_content"] = ""

        styling = _extract_text_styling(layer)
        if styling:
            info["text_styling"] = styling

            font_name = styling.get("font_name", "")
            if font_name:
                if font_name not in state["seen_fonts"]:
                    state["seen_fonts"][font_name] = {
                        "name": font_name,
                        "style": styling.get("font_style", ""),
                        "sizes": [],
                        "tracking": styling.get("tracking", 0),
                    }
                size = styling.get("font_size", 0)
                if size and size not in state["seen_fonts"][font_name]["sizes"]:
                    state["seen_fonts"][font_name]["sizes"].append(size)

            color = styling.get("color")
            if color and color not in state["seen_colors"]:
                state["seen_colors"].add(color)
                state["colors"].append(color)

        text_entry = {"content": info.get("text_content", "")}
        text_entry.update(styling)
        text_entry["bounds"] = info["bounds"]
        if text_entry.get("content"):
            state["text_elements"].append(text_entry)

    return info


def _walk_layers(layer, depth: int, state: dict, structure: list):
    info = _process_layer(layer, depth, state)
    structure.append(info)
    if layer.is_group():
        for child in layer:
            _walk_layers(child, depth + 1, state, structure)


def analyze_psd(file_path: str) -> dict:
    """
    Open and analyze a PSD file without needing Photoshop installed.

    Returns a style guide dict with:
      - canvas dimensions
      - color_palette (hex strings)
      - fonts (name, style, sizes, tracking)
      - text_elements (content + positioning + styling)
      - layer_structure (full tree)
      - design_patterns (typography hierarchy, primary color)
    """
    psd = PSDImage.open(file_path)

    state = {
        "seen_fonts": {},
        "seen_colors": set(),
        "colors": [],
        "text_elements": [],
    }
    structure: list = []

    for layer in psd:
        _walk_layers(layer, 0, state, structure)

    color_palette = list(state["colors"])
    dominant = _extract_dominant_colors(psd)
    for c in dominant:
        if c not in state["seen_colors"]:
            state["seen_colors"].add(c)
            color_palette.append(c)

    fonts = list(state["seen_fonts"].values())

    text_sizes = sorted(
        {te.get("font_size", 0) for te in state["text_elements"] if te.get("font_size")},
        reverse=True,
    )
    typography_hierarchy = {}
    if text_sizes:
        typography_hierarchy["heading_size"] = text_sizes[0]
        if len(text_sizes) > 1:
            typography_hierarchy["subheading_size"] = text_sizes[1]
        if len(text_sizes) > 2:
            typography_hierarchy["body_size"] = text_sizes[-1]

    return {
        "canvas": {"width": psd.width, "height": psd.height},
        "color_palette": color_palette,
        "fonts": fonts,
        "text_elements": state["text_elements"],
        "layer_structure": structure,
        "design_patterns": {
            "primary_color": color_palette[0] if color_palette else "#000000",
            "typography_hierarchy": typography_hierarchy,
            "total_layers": len(structure),
            "text_layer_count": len(state["text_elements"]),
        },
    }


def analyze_folder(folder_path: str) -> dict:
    """
    Analyze every PSD file in a folder and aggregate the results into a
    unified style guide that represents the brand's design language.

    Returns:
      - files_analyzed: list of {file, width, height, status}
      - color_palette: colors ranked by frequency across all files
      - fonts: fonts ranked by usage frequency
      - canvas_sizes: most common dimensions
      - text_elements: all text found across files
      - design_patterns: aggregated typography hierarchy + primary colors
      - raw_analyses: per-file analysis dicts
    """
    psd_files = [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if f.lower().endswith(".psd")
    ]

    if not psd_files:
        return {"error": f"No PSD files found in '{folder_path}'"}

    raw_analyses: list[dict] = []
    files_analyzed: list[dict] = []
    color_counter: Counter = Counter()
    font_counter: Counter = Counter()
    size_counter: Counter = Counter()
    all_text_elements: list[dict] = []

    for fpath in psd_files:
        fname = os.path.basename(fpath)
        try:
            analysis = analyze_psd(fpath)
            raw_analyses.append({"file": fname, **analysis})

            files_analyzed.append({
                "file": fname,
                "width": analysis["canvas"]["width"],
                "height": analysis["canvas"]["height"],
                "status": "ok",
                "layers": analysis["design_patterns"]["total_layers"],
                "text_layers": analysis["design_patterns"]["text_layer_count"],
            })

            for color in analysis["color_palette"]:
                color_counter[color] += 1

            for font in analysis["fonts"]:
                font_counter[font["name"]] += 1

            size_key = f"{analysis['canvas']['width']}x{analysis['canvas']['height']}"
            size_counter[size_key] += 1

            for te in analysis["text_elements"]:
                te["source_file"] = fname
                all_text_elements.append(te)

        except Exception as exc:
            files_analyzed.append({"file": fname, "status": "error", "error": str(exc)})

    # Aggregate color palette — most frequent colors first
    combined_colors = [c for c, _ in color_counter.most_common(20)]

    # Aggregate fonts — most used first, with all observed sizes
    combined_fonts: list[dict] = []
    for font_name, count in font_counter.most_common():
        sizes: list[float] = []
        styles: set[str] = set()
        for ra in raw_analyses:
            for f in ra.get("fonts", []):
                if f["name"] == font_name:
                    sizes.extend(f.get("sizes", []))
                    if f.get("style"):
                        styles.add(f["style"])
        combined_fonts.append({
            "name": font_name,
            "files_used_in": count,
            "styles": sorted(styles),
            "sizes": sorted(set(sizes), reverse=True),
        })

    # Typography hierarchy — pick the most common size bands
    all_sizes: list[float] = []
    for te in all_text_elements:
        s = te.get("font_size", 0)
        if s:
            all_sizes.append(s)

    typography_hierarchy: dict = {}
    if all_sizes:
        unique_sizes = sorted(set(all_sizes), reverse=True)
        if unique_sizes:
            typography_hierarchy["heading_size"] = unique_sizes[0]
        if len(unique_sizes) > 1:
            typography_hierarchy["subheading_size"] = unique_sizes[1]
        if len(unique_sizes) > 2:
            typography_hierarchy["body_size"] = unique_sizes[-1]

    return {
        "total_files": len(psd_files),
        "files_analyzed": files_analyzed,
        "canvas_sizes": [
            {"size": s, "count": c} for s, c in size_counter.most_common()
        ],
        "color_palette": combined_colors,
        "fonts": combined_fonts,
        "text_elements": all_text_elements,
        "design_patterns": {
            "primary_color": combined_colors[0] if combined_colors else "#000000",
            "typography_hierarchy": typography_hierarchy,
            "dominant_font": combined_fonts[0]["name"] if combined_fonts else "",
        },
        "raw_analyses": raw_analyses,
    }
