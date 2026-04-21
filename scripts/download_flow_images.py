"""Download generated images from Google Flow."""
import os
import base64
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
OUTPUT_DIR = r"C:\Users\Estudio Creador\Desktop\Claudecodetest\output\flow_gallery"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

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

        # Get all image srcs
        imgs = flow_page.query_selector_all("img[alt='Imagen generada']")
        print(f"Found {len(imgs)} generated images")

        for i, img in enumerate(imgs):
            src = img.get_attribute("src") or ""
            bbox = img.bounding_box()
            if not src or not bbox:
                continue

            # Fetch image via JavaScript fetch (has same-origin cookies)
            try:
                result = flow_page.evaluate("""async (src) => {
                    try {
                        const resp = await fetch(src);
                        if (!resp.ok) return null;
                        const blob = await resp.blob();
                        return new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onload = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        });
                    } catch(e) {
                        return 'ERROR: ' + e.message;
                    }
                }""", src)

                if result and result.startswith("data:image"):
                    b64 = result.split(",")[1]
                    out_path = os.path.join(OUTPUT_DIR, f"flow_{i:02d}.jpg")
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(b64))
                    print(f"  Saved [{i}]: {out_path} ({len(b64)//1024}KB)")
                else:
                    print(f"  [{i}] Failed: {str(result)[:100]}")
            except Exception as e:
                print(f"  [{i}] Error: {e}")

        print(f"\nDone! Check {OUTPUT_DIR}")


if __name__ == "__main__":
    run()
