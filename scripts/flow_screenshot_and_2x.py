"""Take screenshot of Flow tab and find 2x download options."""
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    ctx = browser.contexts[0]

    flow_page = None
    for page in ctx.pages:
        u = page.url
        if "labs.google" in u or "flow" in u.lower() or "aitestkitchen" in u:
            flow_page = page
            print(f"Found Flow: {u}")
            break

    if not flow_page:
        for page in ctx.pages:
            print(f"  page: {page.url[:80]}")
        raise Exception("No Flow tab found")

    flow_page.bring_to_front()
    time.sleep(1)
    flow_page.screenshot(path="output/_flow_current.png", full_page=False)
    print("Screenshot saved")

    # Find all download buttons
    buttons = flow_page.query_selector_all("button")
    print(f"\nFound {len(buttons)} buttons")
    for btn in buttons:
        txt = btn.inner_text().strip()[:50]
        aria = btn.get_attribute("aria-label") or ""
        if txt or aria:
            print(f"  btn: '{txt}' aria='{aria[:40]}'")

    # Find images with generated content
    imgs = flow_page.query_selector_all("img[alt='Imagen generada']")
    print(f"\nFound {len(imgs)} generated images")
    for i, img in enumerate(imgs):
        src = img.get_attribute("src")
        print(f"  img[{i}]: {src[:80] if src else 'None'}")

    # Look for any links or buttons near images
    download_links = flow_page.query_selector_all("a[download], [aria-label*='download'], [aria-label*='2x'], [aria-label*='Descargar']")
    print(f"\nDownload links: {len(download_links)}")
    for lnk in download_links:
        print(f"  {lnk.get_attribute('aria-label')} / {lnk.inner_text()[:40]}")
