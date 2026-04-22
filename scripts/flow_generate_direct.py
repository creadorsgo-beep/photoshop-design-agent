"""
Direct Flow generation: upload reference + type prompt + submit + download 2x.
"""
import time, base64, os
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
REF_IMG = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\empandas01_ref.jpg"
OUTPUT_DIR = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output"
PROMPT = (
    "empanadas arabes triangulares sobre un plato blanco de ceramica, "
    "sobre una mesada de marmol blanco, fondo limpio, "
    "luz natural lateral suave, fotografia editorial gourmet"
)


def fetch_image(page, src):
    result = page.evaluate("""async (src) => {
        const resp = await fetch(src);
        if (!resp.ok) return null;
        const blob = await resp.blob();
        return new Promise(r => {
            const reader = new FileReader();
            reader.onload = () => r(reader.result);
            reader.readAsDataURL(blob);
        });
    }""", src)
    if result and result.startswith("data:image"):
        return base64.b64decode(result.split(",")[1])
    return None


def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]

        flow_page = next((pg for pg in ctx.pages if "flow" in pg.url and "project" in pg.url), None)
        if not flow_page:
            print("Flow not found!")
            return

        flow_page.bring_to_front()
        time.sleep(1)

        # --- Step 1: Upload reference image ---
        print("Step 1: Uploading reference image...")
        flow_page.screenshot(path=f"{OUTPUT_DIR}/_step1_before.png", timeout=15000)

        # Try to find and use the file upload (hidden input or via button)
        file_inputs = flow_page.query_selector_all("input[type='file']")
        if file_inputs:
            print(f"  Found {len(file_inputs)} file input(s)")
            file_inputs[0].set_input_files(REF_IMG)
            time.sleep(4)
            print("  File set on input.")
        else:
            # Try clicking the add media button and using file chooser
            try:
                with flow_page.expect_file_chooser(timeout=5000) as fc:
                    # Click add button
                    flow_page.locator("button").filter(has_text="add").or_(
                        flow_page.get_by_label("Agregar archivo multimedia")
                    ).first.click()
                fc.value.set_files(REF_IMG)
                time.sleep(4)
                print("  File selected via chooser.")
            except Exception as e:
                print(f"  Could not upload: {e}")

        flow_page.screenshot(path=f"{OUTPUT_DIR}/_step1_after_upload.png", timeout=15000)

        # --- Step 2: Find prompt input ---
        print("\nStep 2: Finding prompt input...")
        prompt_el = None

        # Try multiple selectors
        selectors = [
            "div[contenteditable='true']",
            "textarea",
            "[role='textbox']",
            "div[class*='input']",
        ]
        for sel in selectors:
            els = flow_page.query_selector_all(sel)
            for el in els:
                bb = el.bounding_box()
                if bb and bb['height'] > 20 and bb['width'] > 200:
                    print(f"  Found candidate: {sel} at y={bb['y']:.0f} w={bb['width']:.0f}")
                    prompt_el = el
                    break
            if prompt_el:
                break

        if not prompt_el:
            print("  No prompt input found. Saving page HTML snippet...")
            html = flow_page.evaluate("document.body.innerHTML.substring(0, 3000)")
            with open(f"{OUTPUT_DIR}/_flow_html.txt", "w", encoding="utf-8", errors="replace") as f:
                f.write(html)
            return

        # --- Step 3: Type prompt ---
        print(f"\nStep 3: Typing prompt...")
        prompt_el.click()
        time.sleep(0.3)
        # Clear existing content
        prompt_el.press("Control+a")
        prompt_el.press("Delete")
        time.sleep(0.2)
        prompt_el.type(PROMPT, delay=20)
        time.sleep(0.5)

        flow_page.screenshot(path=f"{OUTPUT_DIR}/_step3_prompt.png", timeout=15000)
        print(f"  Prompt typed: {PROMPT[:60]}...")

        # --- Step 4: Submit ---
        print("\nStep 4: Submitting...")
        # Look for arrow/send button near the prompt
        arrow_btns = flow_page.query_selector_all("button")
        for btn in arrow_btns:
            bb = btn.bounding_box()
            if not bb:
                continue
            aria = btn.get_attribute("aria-label") or ""
            txt = btn.inner_text() or ""
            # Check for buttons near the bottom with arrow icon
            if "arrow" in aria.lower() or "enviar" in aria.lower() or "submit" in aria.lower():
                print(f"  Clicking '{aria[:40]}'")
                btn.click()
                break
        else:
            # Press Enter
            print("  Pressing Enter...")
            prompt_el.press("Enter")

        flow_page.screenshot(path=f"{OUTPUT_DIR}/_step4_submitted.png", timeout=15000)

        # --- Step 5: Wait for generation ---
        print("\nStep 5: Waiting 90s for generation...")
        time.sleep(90)

        flow_page.screenshot(path=f"{OUTPUT_DIR}/_step5_after_gen.png", timeout=15000)
        print("  Screenshot after generation saved.")

        # --- Step 6: Download new images at 2x ---
        print("\nStep 6: Downloading new images at 2x...")
        imgs = flow_page.query_selector_all("img[alt='Imagen generada']")
        print(f"  Total generated images: {len(imgs)}")

        # Download first 4 (most recent)
        downloaded = []
        for i, img in enumerate(imgs[:4]):
            src = img.get_attribute("src") or ""
            if not src:
                continue

            # Download 2x: For Flow, images are served via redirect
            # The redirect goes to the actual CDN URL which is full resolution
            # We can try appending size params or just download as-is (full res)
            data = fetch_image(flow_page, src)
            if data:
                out = os.path.join(OUTPUT_DIR, f"palau_emp_marmol_{i:02d}.jpg")
                with open(out, "wb") as f:
                    f.write(data)
                kb = len(data) // 1024
                downloaded.append(out)
                print(f"  [{i}] Saved: {out} ({kb}KB)")
            else:
                print(f"  [{i}] Failed")

        print(f"\nDownloaded {len(downloaded)} images")
        if downloaded:
            print(f"Best: {downloaded[0]}")
        print("Done!")


if __name__ == "__main__":
    run()
