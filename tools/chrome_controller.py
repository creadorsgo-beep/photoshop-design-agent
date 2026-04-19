"""
Chrome automation for Google Labs Flow image generation.

Connects to an existing Chrome instance via CDP (remote debugging port 9222).
To enable: restart Chrome with --remote-debugging-port=9222
  Windows shortcut: chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/temp/chrome-debug

Usage:
  from tools.chrome_controller import generate_image_flow
  result = generate_image_flow("cinematic photo of a coffee shop at sunset")
"""

import os
import time
import base64
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

FLOW_URL = "https://labs.google/flow/image-generation"
CDP_URL = "http://localhost:9222"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _connect(p):
    """Connect to existing Chrome via CDP, or raise with instructions."""
    try:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        return browser
    except Exception:
        raise RuntimeError(
            "No se pudo conectar a Chrome en el puerto 9222.\n"
            "Abre Chrome con:\n"
            "  chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/temp/chrome-debug\n"
            "O cierra Chrome y ejecuta: scripts/launch_chrome_debug.bat"
        )


def _get_or_create_page(browser, url: str):
    """Find existing Flow tab or open a new one."""
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    for page in context.pages:
        if "labs.google" in page.url or "flow" in page.url.lower():
            return page
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    return page


def _find_prompt_input(page):
    """Try multiple selectors to find the prompt textarea."""
    selectors = [
        "textarea[placeholder*='prompt' i]",
        "textarea[placeholder*='describe' i]",
        "textarea[placeholder*='image' i]",
        "textarea[aria-label*='prompt' i]",
        "[contenteditable='true'][aria-label*='prompt' i]",
        "textarea",
        "[contenteditable='true']",
    ]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=1000):
                return el
        except Exception:
            continue
    return None


def _find_generate_button(page):
    """Find the generate/submit button."""
    selectors = [
        "button[aria-label*='generate' i]",
        "button[aria-label*='create' i]",
        "button:has-text('Generate')",
        "button:has-text('Create')",
        "button:has-text('Run')",
        "[role='button']:has-text('Generate')",
        "button[type='submit']",
    ]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=500):
                return el
        except Exception:
            continue
    return None


def _wait_for_image(page, timeout_ms: int = 60000) -> list[str]:
    """Wait for generated images to appear and return their src URLs."""
    # Wait for any new images to load
    start = time.time()
    while (time.time() - start) * 1000 < timeout_ms:
        images = page.locator("img[src*='blob:'], img[src*='data:'], img[src*='generated'], img[src*='output']").all()
        if images:
            srcs = []
            for img in images:
                src = img.get_attribute("src") or ""
                if src and src not in srcs:
                    srcs.append(src)
            if srcs:
                return srcs
        time.sleep(1)
    return []


def _save_screenshot(page, name: str) -> str:
    """Save a debug screenshot and return the path."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = str(OUTPUT_DIR / f"_debug_{name}.png")
    page.screenshot(path=path)
    return path


def _download_image(page, img_src: str, output_path: str) -> bool:
    """Download an image from blob or URL to disk."""
    if img_src.startswith("blob:") or img_src.startswith("data:"):
        # Use JS to convert to base64
        b64 = page.evaluate("""async (src) => {
            const res = await fetch(src);
            const buf = await res.arrayBuffer();
            return btoa(String.fromCharCode(...new Uint8Array(buf)));
        }""", img_src)
        if b64:
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64))
            return True
    return False

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image_flow(
    prompt: str,
    output_path: str = "",
    style_suffix: str = "",
    wait_seconds: int = 60,
) -> dict:
    """
    Generate an image via Google Labs Flow using an existing Chrome session.

    Args:
        prompt: The image generation prompt (will be enhanced intelligently)
        output_path: Where to save the PNG. Auto-generated if empty.
        style_suffix: Extra style keywords appended to prompt (e.g. "cinematic, 8k, photorealistic")
        wait_seconds: Max seconds to wait for generation

    Returns:
        dict with keys: success, path, prompt_used, screenshot, error
    """
    full_prompt = prompt.strip()
    if style_suffix:
        full_prompt = f"{full_prompt}, {style_suffix.strip()}"

    if not output_path:
        safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:40]).strip("_")
        output_path = str(OUTPUT_DIR / f"flow_{safe_name}.png")

    OUTPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = _connect(p)
        except RuntimeError as e:
            return {"success": False, "error": str(e), "path": None}

        page = _get_or_create_page(browser, FLOW_URL)
        time.sleep(2)

        # Navigate to Flow if not already there
        if "labs.google" not in page.url and "flow" not in page.url.lower():
            page.goto(FLOW_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

        screenshot_before = _save_screenshot(page, "before")

        # Find and fill prompt
        prompt_input = _find_prompt_input(page)
        if not prompt_input:
            screenshot = _save_screenshot(page, "no_input")
            return {
                "success": False,
                "error": "No se encontró campo de prompt. Ver screenshot de diagnóstico.",
                "screenshot": screenshot,
                "path": None,
                "current_url": page.url,
            }

        prompt_input.click()
        prompt_input.fill("")
        prompt_input.fill(full_prompt)
        time.sleep(0.5)

        # Find and click generate button
        gen_btn = _find_generate_button(page)
        if gen_btn:
            gen_btn.click()
        else:
            # Try pressing Enter/Ctrl+Enter as fallback
            prompt_input.press("Enter")

        time.sleep(2)
        screenshot_generating = _save_screenshot(page, "generating")

        # Wait for images
        imgs = _wait_for_image(page, timeout_ms=wait_seconds * 1000)

        screenshot_after = _save_screenshot(page, "after")

        if not imgs:
            return {
                "success": False,
                "error": f"No se generaron imágenes en {wait_seconds}s.",
                "screenshot": screenshot_after,
                "prompt_used": full_prompt,
                "path": None,
            }

        # Download first generated image
        downloaded = False
        for src in imgs:
            if _download_image(page, src, output_path):
                downloaded = True
                break

        if not downloaded:
            # Fallback: screenshot the result area
            page.screenshot(path=output_path)

        return {
            "success": True,
            "path": output_path,
            "prompt_used": full_prompt,
            "images_found": len(imgs),
            "screenshot": screenshot_after,
        }


def take_flow_screenshot() -> dict:
    """Take a screenshot of the current Flow page for debugging."""
    with sync_playwright() as p:
        try:
            browser = _connect(p)
        except RuntimeError as e:
            return {"success": False, "error": str(e)}

        page = _get_or_create_page(browser, FLOW_URL)
        time.sleep(1)
        path = _save_screenshot(page, "inspect")
        return {
            "success": True,
            "screenshot": path,
            "url": page.url,
            "title": page.title(),
        }


def explore_flow_ui() -> dict:
    """
    Explore the current Flow page and return UI elements found.
    Useful for diagnosing selector issues.
    """
    with sync_playwright() as p:
        try:
            browser = _connect(p)
        except RuntimeError as e:
            return {"success": False, "error": str(e)}

        page = _get_or_create_page(browser, FLOW_URL)
        time.sleep(1)

        inputs = page.evaluate("""() => {
            const els = [...document.querySelectorAll('textarea, [contenteditable], input[type=text]')];
            return els.map(e => ({
                tag: e.tagName,
                placeholder: e.placeholder || '',
                ariaLabel: e.getAttribute('aria-label') || '',
                id: e.id || '',
                className: e.className.substring(0, 80),
            }));
        }""")

        buttons = page.evaluate("""() => {
            const els = [...document.querySelectorAll('button, [role=button]')];
            return els.slice(0, 20).map(e => ({
                text: e.innerText.substring(0, 50),
                ariaLabel: e.getAttribute('aria-label') || '',
                id: e.id || '',
            }));
        }""")

        screenshot = _save_screenshot(page, "explore")
        return {
            "success": True,
            "url": page.url,
            "title": page.title(),
            "inputs": inputs,
            "buttons": buttons,
            "screenshot": screenshot,
        }
