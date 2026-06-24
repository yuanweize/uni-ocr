import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    pdf_path = "/Users/yuanweize/.gemini/antigravity-ide/brain/e23a41be-b395-4d79-944d-bcabb7c89149/media__1782307327540.pdf"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 1000})
        page = await context.new_page()

        # Login
        print("Navigating to login...")
        await page.goto("http://localhost:8000/login")
        await page.fill("input[type=\"password\"]", "admin123")
        await page.click("button[type=\"submit\"]")
        await page.wait_for_timeout(2000)

        # Dashboard / OcrConsole
        print("Navigating to dashboard...")
        await page.goto("http://localhost:8000/")
        await page.wait_for_timeout(2000)
        
        # Upload the user's PDF to trigger extraction and result view
        print("Uploading PDF...")
        # change format to pdf first
        # wait, the default might be markdown, we need to click the format selector.
        # But wait, extraction produces markdown/json/pdf depending on format. 
        # The user said "Searchable PDF然后执行F. Run Extraction"
        # So we should click the "PDF" format button.
        await page.click("button:has-text('Searchable PDF')")
        
        await page.set_input_files('input[type="file"]', pdf_path)
        await page.wait_for_timeout(500)
        await page.click("button:has-text('Run Extraction')")
        
        # Wait a long time for extraction and rendering
        print("Waiting for extraction...")
        await page.wait_for_timeout(10000)

        print("Capturing dashboard...")
        await page.screenshot(path="assets/dashboard.png", full_page=False)

        # Settings
        print("Navigating to settings...")
        await page.goto("http://localhost:8000/settings")
        await page.wait_for_timeout(2000)
        print("Capturing settings...")
        await page.screenshot(path="assets/settings.png", full_page=False)

        await browser.close()
        print("Screenshots captured!")

asyncio.run(main())
