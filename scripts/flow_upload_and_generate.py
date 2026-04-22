"""
Upload reference image to Flow, generate empanadas on marble, download at 2x.
"""
import time, base64, os
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
REF_IMG = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\empandas01_ref.jpg"
OUTPUT_DIR = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output"
FLOW_URL = "https://labs.google/fx/es-419/tools/flow/project/24f0781a-531a-443a-9ea1-e5e792dbe0a2"

PROMPT = (
    "empanadas arabes triangulares sobre un plato blanco de ceramica, "
    "apoyado sobre una mesada de marmol blanco con vetas grises, "
    "fondo limpio neutro, luz natural lateral suave, "
    "fotografia editorial de alimentos estilo gourmet, "
    "shallow depth of field, Canon 5D 85mm"
)


def save_img_from_page(page, src, out_path):
    """Fetch image via page context (has session cookies) and save to disk."""
    result = page.evaluate("""async (src) => {
        try {
            const resp = await fetch(src);
            if (!resp.ok) return null;
            const blob = await resp.blob();
            return new Promise(resolve => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.readAsDataURL(blob);
            });
        } catch(e) { return 'ERROR:' + e.message; }
    }""", src)
    if result and result.startswith("data:image"):
        b64 = result.split(",")[1]
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
        return True
    return False


def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]

        # Find Flow tab
        flow_page = None
        for page in ctx.pages:
            if "flow" in page.url and "project" in page.url:
                flow_page = page
                break
        if not flow_page:
            print("Flow tab not found!")
            return

        flow_page.bring_to_front()
        time.sleep(1)
        print("Flow tab found:", flow_page.url[:60])

        # Take screenshot before
        flow_page.screenshot(path=f"{OUTPUT_DIR}/_flow_before_upload.png", timeout=15000)

        # Look for file upload input or the "Add media" button
        # Flow's upload mechanism: find file input or the add button
        print("\nLooking for upload mechanism...")

        # Try to find file input
        file_inputs = flow_page.query_selector_all("input[type='file']")
        print(f"  File inputs found: {len(file_inputs)}")

        if file_inputs:
            print("  Using file input directly...")
            file_inputs[0].set_input_files(REF_IMG)
            time.sleep(3)
        else:
            # Click "Add media" button and then handle file dialog
            print("  Looking for Add media button...")
            # Button with 'add' or 'Agregar'
            btns = flow_page.query_selector_all("button")
            for btn in btns:
                txt = btn.inner_text() or ""
                aria = btn.get_attribute("aria-label") or ""
                if "agregar" in txt.lower() or "add" in aria.lower() or "upload" in aria.lower():
                    print(f"    Found: '{txt[:40]}' aria='{aria[:40]}'")

            # Try clicking the add media button (Agregar archivo multimedia)
            add_btn = flow_page.get_by_label("Agregar archivo multimedia")
            if add_btn.count() > 0:
                print("  Clicking 'Agregar archivo multimedia'...")
                # Use expect_file_chooser to handle the dialog
                with flow_page.expect_file_chooser() as fc_info:
                    add_btn.first.click()
                file_chooser = fc_info.value
                file_chooser.set_files(REF_IMG)
                print("  File selected!")
                time.sleep(3)
            else:
                print("  Add button not found by label, trying by text...")
                # Try by text
                try:
                    with flow_page.expect_file_chooser(timeout=5000) as fc_info:
                        flow_page.locator("button:has-text('add')").first.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(REF_IMG)
                    time.sleep(3)
                except Exception as e:
                    print(f"  Could not find upload button: {e}")

        # Take screenshot after upload attempt
        flow_page.screenshot(path=f"{OUTPUT_DIR}/_flow_after_upload.png", timeout=15000)
        print("Screenshot after upload saved.")

        # Now find the prompt input and type the generation prompt
        print("\nEntering generation prompt...")
        prompt_input = None

        # Try common selectors for the prompt area
        for selector in ["textarea", "[placeholder*='crear']", "[placeholder*='Qué']",
                         "[aria-label*='crear']", "[aria-label*='prompt']", ".sc-68b42f2-2"]:
            els = flow_page.query_selector_all(selector)
            if els:
                print(f"  Found {len(els)} elements for '{selector}'")
                prompt_input = els[0]
                break

        if prompt_input:
            prompt_input.click()
            time.sleep(0.3)
            prompt_input.fill(PROMPT)
            time.sleep(0.5)
            print(f"  Prompt entered: {PROMPT[:60]}...")

            # Take screenshot
            flow_page.screenshot(path=f"{OUTPUT_DIR}/_flow_prompt_entered.png", timeout=15000)

            # Submit (Enter key or click generate button)
            print("  Submitting generation...")
            # Look for submit/generate button
            submit_btns = flow_page.query_selector_all("button")
            for btn in submit_btns:
                aria = btn.get_attribute("aria-label") or ""
                txt = btn.inner_text() or ""
                if "generar" in txt.lower() or "crear" in txt.lower() or "submit" in aria.lower() or "send" in aria.lower() or "arrow" in aria.lower():
                    print(f"    Clicking '{txt[:30]}' aria='{aria[:30]}'")
                    btn.click()
                    break
            else:
                # Press Enter
                print("  Pressing Enter to submit...")
                prompt_input.press("Enter")

            print(f"\nWaiting 120s for generation...")
            time.sleep(120)

            # Take screenshot to see result
            flow_page.screenshot(path=f"{OUTPUT_DIR}/_flow_after_gen.png", timeout=15000)
            print("Screenshot after generation saved.")

        else:
            print("  Prompt input not found!")
            return

        # Download generated images at 2x
        print("\nLooking for generated images to download at 2x...")
        imgs = flow_page.query_selector_all("img[alt='Imagen generada']")
        print(f"  Found {len(imgs)} generated images")

        # Get the most recent ones (first in list = most recently generated)
        downloaded = []
        for i, img in enumerate(imgs[:8]):
            src = img.get_attribute("src") or ""
            bbox = img.bounding_box()
            if not src or not bbox:
                continue

            # Get image at 2x via the API URL with size parameter
            # Flow uses /fx/api/trpc/media.getMediaUrlRedirect?name=...
            # Try to get a larger version
            name_param = src.split("name=")[-1] if "name=" in src else ""

            # Fetch at 2x by requesting the full resolution
            out_path = os.path.join(OUTPUT_DIR, f"flow_marmol_2x_{i:02d}.jpg")
            if save_img_from_page(flow_page, src, out_path):
                size = os.path.getsize(out_path)
                downloaded.append(out_path)
                print(f"  Saved [{i}]: {out_path} ({size//1024}KB)")
            else:
                print(f"  [{i}] Failed to download")

        print(f"\nDownloaded {len(downloaded)} images")
        if downloaded:
            print(f"Best candidate: {downloaded[0]}")

        print("\nDone!")


if __name__ == "__main__":
    run()
