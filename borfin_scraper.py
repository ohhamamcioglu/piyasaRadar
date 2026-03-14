import asyncio
from playwright.async_api import async_playwright
import json
import os
from dotenv import load_dotenv

# Load credentials from .env_borfin
load_dotenv(".env_borfin")
BORFIN_EMAIL = os.getenv("BORFIN_EMAIL")
BORFIN_PASSWORD = os.getenv("BORFIN_PASSWORD")

async def scrape_courses():
    if not BORFIN_EMAIL or not BORFIN_PASSWORD:
        print("Error: BORFIN_EMAIL or BORFIN_PASSWORD not found in .env_borfin")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Navigating to Borfin login page...")
        await page.goto("https://borfin.com/tr/auth/sign-in")
        await page.wait_for_load_state("networkidle")

        # Handle cookie modal if it exists
        try:
            cookie_btn = page.locator("button:has-text('Kabul Ediyorum')")
            if await cookie_btn.is_visible(timeout=3000):
                print("Accepting cookies...")
                await cookie_btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass # No cookie modal

        print("Filling in credentials...")
        try:
            # Wait for the email input to be visible and ready
            await page.wait_for_selector("input[name='email']", state="visible", timeout=10000)
            
            await page.fill("input[name='email']", BORFIN_EMAIL)
            await page.fill("input[name='password']", BORFIN_PASSWORD)
            
            print("Clicking login button...")
            await page.click("button:has-text('Giriş yap')")
            
            # Wait for navigation after login
            print("Waiting for dashboard to load...")
            await page.wait_for_url("**/panel**", timeout=15000)
            print("Successfully logged in!")
            
            print("Navigating to Courses page...")
            await page.goto("https://borfin.com/tr/panel/courses")
            await page.wait_for_load_state("networkidle")
            
            # Take a screenshot of the courses page
            await page.screenshot(path="borfin_courses.png", full_page=True)

            print("Extracting course HTML for analysis...")
            html_content = await page.content()
            with open("borfin_courses.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            print("Extraction complete. Browser closing.")
        
        except Exception as e:
            print(f"Error during login or navigation: {e}")
            await page.screenshot(path="borfin_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_courses())
