"""Read the spreadsheet tab open in Chrome via CDP."""
import time, base64
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"

def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]

        # List all pages
        print("Open tabs:")
        for i, page in enumerate(ctx.pages):
            print(f"  [{i}] {page.url[:80]}")

        # Find spreadsheet tab
        sheet_page = None
        for page in ctx.pages:
            u = page.url
            if "spreadsheet" in u or "docs.google.com" in u or "sheets" in u:
                sheet_page = page
                print(f"\nFound sheet: {u}")
                break

        if not sheet_page:
            print("No spreadsheet found — taking screenshot of all tabs")
            for i, page in enumerate(ctx.pages):
                try:
                    page.bring_to_front()
                    time.sleep(0.5)
                    page.screenshot(path=f"output/_tab_{i}.png", timeout=10000)
                    print(f"  Screenshot tab {i}: {page.url[:60]}")
                except Exception as e:
                    print(f"  Tab {i} failed: {e}")
            return

        sheet_page.bring_to_front()
        time.sleep(1)
        sheet_page.screenshot(path="output/_sheet.png", timeout=15000)
        print("Screenshot saved: output/_sheet.png")

        # Try to extract text content
        try:
            text = sheet_page.evaluate("""() => {
                // Get all cell values visible in the sheet
                var cells = document.querySelectorAll('.cell-content, [class*="cell"], td');
                var texts = [];
                cells.forEach(function(c) {
                    var t = c.innerText || c.textContent;
                    if (t && t.trim()) texts.push(t.trim());
                });
                return texts.slice(0, 200).join(' | ');
            }""")
            print("\nCell content:", text[:2000])
        except Exception as e:
            print("Text extract error:", e)

if __name__ == "__main__":
    run()
