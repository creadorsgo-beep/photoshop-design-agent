"""Download the first successfully generated image from Google Flow."""
import os
import time
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
FLOW_URL = "https://labs.google/fx/es-419/tools/flow/project/24f0781a-531a-443a-9ea1-e5e792dbe0a2"
OUTPUT = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\palau_marmol_bg.jpg"


def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

        # Find the Flow tab
        flow_page = None
        for page in context.pages:
            if "flow" in page.url:
                flow_page = page
                break

        if not flow_page:
            print("Flow tab not found!")
            return

        print(f"Found Flow tab: {flow_page.url}")
        flow_page.bring_to_front()
        time.sleep(1)

        # Screenshot before clicking
        flow_page.screenshot(path="output/_before_click.png")

        # Find all images in the grid
        imgs = flow_page.query_selector_all("img")
        print(f"Found {len(imgs)} img elements")
        for i, img in enumerate(imgs):
            src = img.get_attribute("src") or ""
            alt = img.get_attribute("alt") or ""
            bbox = img.bounding_box()
            print(f"  [{i}] alt={alt[:50]} src={src[:80]} bbox={bbox}")

        # Click on first content image (skip icons)
        content_imgs = [img for img in imgs if "blob:" in (img.get_attribute("src") or "")
                        or "googleusercontent" in (img.get_attribute("src") or "")
                        or img.bounding_box() and img.bounding_box()['width'] > 50]

        print(f"\nContent images: {len(content_imgs)}")

        if content_imgs:
            first_img = content_imgs[0]
            bbox = first_img.bounding_box()
            print(f"Clicking image at: {bbox}")
            first_img.click()
            time.sleep(2)

            # Screenshot after click
            flow_page.screenshot(path="output/_after_click.png")
            print("Screenshot saved: output/_after_click.png")

            # Look for download button or larger image
            download_btns = flow_page.query_selector_all("button")
            for btn in download_btns:
                text = btn.inner_text() or ""
                if "download" in text.lower() or "descargar" in text.lower() or "download" in (btn.get_attribute("aria-label") or "").lower():
                    print(f"Download button found: {text}")
                    btn.click()
                    time.sleep(2)
                    break

            # Try to get the image src and download it
            large_imgs = flow_page.query_selector_all("img")
            for img in large_imgs:
                src = img.get_attribute("src") or ""
                bbox = img.bounding_box()
                if bbox and bbox['width'] > 200:
                    print(f"Large img src: {src[:120]}, size: {bbox['width']}x{bbox['height']}")
                    if src.startswith("blob:") or "usercontent" in src or "lh3.google" in src:
                        # Try to download via JS
                        try:
                            img_data = flow_page.evaluate("""(src) => {
                                return new Promise((resolve) => {
                                    const img = document.createElement('img');
                                    img.crossOrigin = 'anonymous';
                                    img.onload = () => {
                                        const canvas = document.createElement('canvas');
                                        canvas.width = img.naturalWidth;
                                        canvas.height = img.naturalHeight;
                                        canvas.getContext('2d').drawImage(img, 0, 0);
                                        resolve(canvas.toDataURL('image/jpeg', 0.95));
                                    };
                                    img.onerror = () => resolve(null);
                                    img.src = src;
                                });
                            }""", src)
                            if img_data and img_data.startswith("data:image"):
                                b64 = img_data.split(",")[1]
                                out = OUTPUT.replace(".jpg", f"_canvas.jpg")
                                with open(out, "wb") as f:
                                    f.write(base64.b64decode(b64))
                                print(f"Saved via canvas: {out}")
                        except Exception as e:
                            print(f"Canvas error: {e}")

        # Final screenshot
        flow_page.screenshot(path="output/_flow_final.png")
        print("Done!")


if __name__ == "__main__":
    run()
