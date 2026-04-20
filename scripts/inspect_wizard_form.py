import sys, time
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

OVERVIEW_URL = "https://console.cloud.google.com/auth/overview?project=gen-lang-client-0603163008"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    ctx = browser.contexts[0]
    page = None
    for pg in ctx.pages:
        if 'console.cloud.google.com' in pg.url:
            page = pg
            break
    if not page:
        page = ctx.new_page()

    page.goto(OVERVIEW_URL, wait_until='domcontentloaded', timeout=30000)
    time.sleep(3)
    print("Page:", page.url)

    # Click Comenzar
    comenzar = page.locator("button:has-text('Comenzar')").first
    print("Comenzar visible:", comenzar.is_visible(timeout=3000))
    comenzar.click()
    time.sleep(5)  # Wait longer
    print("After click URL:", page.url)
    page.screenshot(path='credentials/_w1_after_comenzar.png')

    # Wait for form
    try:
        page.wait_for_selector("input, mat-select, form", timeout=10000)
        print("Form element found")
    except Exception as e:
        print("No form element:", e)

    time.sleep(2)
    page.screenshot(path='credentials/_w2_form.png')

    # Inspect
    elements = page.evaluate("""() => {
        const res = [];
        document.querySelectorAll('mat-select, input, select, textarea').forEach(el => {
            res.push({
                tag: el.tagName,
                id: el.id || '',
                fcn: el.getAttribute('formcontrolname') || '',
                placeholder: el.placeholder || el.getAttribute('placeholder') || '',
                ariaLabel: el.getAttribute('aria-label') || '',
                text: el.innerText ? el.innerText.substring(0,40) : (el.value || '').substring(0,40)
            });
        });
        return res;
    }""")
    print(f"Elements found: {len(elements)}")
    for el in elements:
        print(" ", el)
