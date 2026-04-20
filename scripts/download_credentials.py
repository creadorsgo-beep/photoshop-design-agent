"""
Automates downloading OAuth 2.0 credentials from Google Auth Platform (new GCP UI, Spanish).
Connects to existing Chrome debug session on port 9222.
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
PROJECT_ID = "gen-lang-client-0603163008"
SUPPORT_EMAIL = "creadorsgo@gmail.com"
CREDS_DIR = Path(__file__).parent.parent / "credentials"
OUTPUT_FILE = CREDS_DIR / "credentials.json"

AUTH_BASE = "https://console.cloud.google.com/auth"
CLIENTS_URL = f"{AUTH_BASE}/clients?project={PROJECT_ID}"
OVERVIEW_URL = f"{AUTH_BASE}/overview?project={PROJECT_ID}"


def ss(page, name):
    path = str(CREDS_DIR / f"_s_{name}.png")
    page.screenshot(path=path)
    print(f"  [ss] {name}")


def dismiss_search(page):
    page.keyboard.press("Escape")
    time.sleep(0.2)


def setup_auth_platform(page):
    """Complete the Google Auth Platform setup wizard."""
    print("  Starting setup wizard...")

    comenzar = page.locator(
        "button:has-text('Comenzar'), a:has-text('Comenzar'), "
        "button:has-text('Get started')"
    ).first
    comenzar.wait_for(state="visible", timeout=8000)
    comenzar.click()
    time.sleep(3)
    ss(page, "02_wizard_start")

    # Step 1: App information
    # Fill app name (text input)
    app_name = page.locator("input[placeholder*='Nombre' i], input[placeholder*='name' i]").first
    if not app_name.is_visible(timeout=3000):
        # Locate by being inside the form area — avoid header search bar
        app_name = page.locator("section input, form input").first
    if app_name.is_visible(timeout=3000):
        app_name.click()
        time.sleep(0.2)
        dismiss_search(page)
        app_name.click()
        app_name.fill("Photoshop Design Agent")
        print("  App name filled")

    # Support email dropdown (mat-select, not text input)
    email_select = page.locator(
        "mat-select[placeholder*='Correo' i], "
        "mat-select[placeholder*='email' i], "
        "mat-select[placeholder*='correo' i]"
    ).first
    if not email_select.is_visible(timeout=3000):
        # It may just be the second mat-select or the only one
        email_select = page.locator("mat-select").first

    if email_select.is_visible(timeout=3000):
        print("  Opening email dropdown...")
        email_select.click()
        time.sleep(1)
        ss(page, "03_email_dropdown")
        # Click the email option in the overlay
        email_opt = page.locator(f"mat-option:has-text('{SUPPORT_EMAIL}')").first
        email_opt.wait_for(state="visible", timeout=5000)
        email_opt.click()
        print(f"  Email selected: {SUPPORT_EMAIL}")
    else:
        print("  WARNING: email dropdown not found")
        ss(page, "03_no_email")

    ss(page, "04_step1_ready")

    # Click Siguiente for each wizard step
    for step_i in range(6):
        siguiente = page.locator(
            "button:has-text('Siguiente'), button:has-text('Next')"
        ).first
        if siguiente.is_visible(timeout=3000):
            siguiente.click()
            time.sleep(2)
            ss(page, f"05_step{step_i+1}")

            # If this step has additional required fields, handle them
            body = page.inner_text("body")
            # Step: Público — select user type or just continue
            # Step: Información de contacto — may need developer email
            if "contacto" in body.lower() or "contact" in body.lower():
                dev_input = page.locator(
                    "input[placeholder*='email' i][type='email'], "
                    "input[formcontrolname*='email' i]"
                ).last
                if dev_input.is_visible(timeout=2000):
                    dev_input.fill(SUPPORT_EMAIL)
                    print(f"  Dev contact email: {SUPPORT_EMAIL}")
        else:
            # Check for a Finish/Save button
            finish = page.locator(
                "button:has-text('Guardar y continuar'), "
                "button:has-text('Save and continue'), "
                "button:has-text('Terminar'), button:has-text('Finish')"
            ).first
            if finish.is_visible(timeout=2000):
                finish.click()
                time.sleep(2)
                ss(page, f"05_finish{step_i}")
            break

    ss(page, "06_wizard_done")


def run():
    CREDS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]

        page = None
        for pg in ctx.pages:
            if "console.cloud.google.com" in pg.url:
                page = pg
                break
        if not page:
            page = ctx.new_page()

        # ---------------------------------------------------------------
        # Phase 1: Ensure Auth Platform is configured
        # ---------------------------------------------------------------
        print("Checking Auth Platform...")
        page.goto(OVERVIEW_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        ss(page, "01_overview")

        body = page.inner_text("body")
        if (
            "comenzar" in body.lower()
            or "get started" in body.lower()
            or "no se configuro" in body.lower()
        ):
            setup_auth_platform(page)
            # Navigate back to clients after setup
            page.goto(CLIENTS_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

        # ---------------------------------------------------------------
        # Phase 2: Create OAuth Client
        # ---------------------------------------------------------------
        print("Clients page...")
        ss(page, "10_clients")

        # Check if already has clients
        body = page.inner_text("body")
        if "no se configuro" in body.lower() or "comenzar" in body.lower():
            print("  Still need to complete setup — trying Comenzar on clients page...")
            setup_auth_platform(page)
            page.goto(CLIENTS_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            ss(page, "10b_clients_retry")

        print("Clicking Crear cliente...")
        create_btn = page.locator(
            "button:has-text('Crear cliente'), button:has-text('Create client'), "
            "a:has-text('Crear cliente'), a:has-text('Create client')"
        ).first
        create_btn.wait_for(state="visible", timeout=15000)
        create_btn.click()
        time.sleep(3)
        ss(page, "11_create_form")

        # Select Desktop app type
        type_select = page.locator("mat-select").first
        if type_select.is_visible(timeout=5000):
            print("  Opening type dropdown...")
            type_select.click()
            time.sleep(1)
            ss(page, "12_type_open")
            desktop = page.locator(
                "mat-option:has-text('App de escritorio'), "
                "mat-option:has-text('Desktop app')"
            ).first
            desktop.wait_for(state="visible", timeout=5000)
            desktop.click()
            time.sleep(0.5)
            print("  Desktop app selected")

        # Fill client name
        dismiss_search(page)
        name_field = page.locator(
            "input[formcontrolname='name'], input[formcontrolname='displayName'], "
            "input[placeholder*='nombre' i], input[placeholder*='name' i]"
        ).first
        if name_field.is_visible(timeout=3000):
            name_field.click()
            time.sleep(0.2)
            dismiss_search(page)
            name_field.click()
            name_field.fill("photoshop-design-agent")
            print("  Client name filled")
        else:
            all_inputs = page.locator("input:visible").all()
            print(f"  No name field found. Visible inputs: {len(all_inputs)}")

        ss(page, "13_before_submit")

        # Submit
        submit = page.locator(
            "button[type='submit']:visible, button:has-text('Crear'):visible"
        ).last
        submit.wait_for(state="visible", timeout=10000)
        submit.click()
        time.sleep(5)
        ss(page, "14_after_submit")

        # Download JSON from dialog/page
        print("Looking for Download JSON...")
        dl_btn = page.locator(
            "a:has-text('Descargar JSON'), a:has-text('Download JSON'), "
            "button:has-text('Descargar JSON'), button:has-text('Download JSON')"
        ).first
        dl_btn.wait_for(state="visible", timeout=15000)
        ss(page, "15_download_ready")

        with page.expect_download(timeout=15000) as dl_info:
            dl_btn.click()

        download = dl_info.value
        download.save_as(str(OUTPUT_FILE))
        print(f"Saved: {OUTPUT_FILE}")

        # Dismiss dialog
        try:
            page.locator(
                "button:has-text('Aceptar'), button:has-text('OK'), "
                "button:has-text('Listo'), button:has-text('Done')"
            ).first.click()
        except Exception:
            pass

        # Validate
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        key = data.get("installed", data.get("web", {})).get("client_id", "?")
        print(f"client_id: {key[:50]}...")
        print("credentials.json ready.")


if __name__ == "__main__":
    run()
