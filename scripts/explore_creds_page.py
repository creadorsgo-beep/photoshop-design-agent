import sys, time
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

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
        page.goto('https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0603163008', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2)
    print('URL:', page.url)

    btns = page.evaluate("""() => {
        return [...document.querySelectorAll('button, a[role=button], [role=button]')].slice(0, 40).map(e => ({
            text: e.innerText.substring(0,60).replace(/\\s+/g,' ').trim(),
            ariaLabel: e.getAttribute('aria-label') || '',
            id: e.id || '',
            cls: e.className.substring(0,60)
        }))
    }""")
    for b in btns:
        if b['text'] or b['ariaLabel']:
            print('BTN:', b)

    page.screenshot(path='credentials/_explore_creds.png')
    print('Screenshot saved to credentials/_explore_creds.png')
