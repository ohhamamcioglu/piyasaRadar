#!/usr/bin/env python3
"""
Borfin Transcript Extractor 🎬📝
Extracts WebVTT subtitles from all lessons in Borfin courses.
Uses Playwright to login, navigate courses, and intercept .vtt network requests.
"""
import asyncio
import json
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv(".env_borfin")
BORFIN_EMAIL = os.getenv("BORFIN_EMAIL")
BORFIN_PASSWORD = os.getenv("BORFIN_PASSWORD")

# High priority course IDs (extracted from scraping)
COURSE_IDS = [
    {"id": "2466", "title": "PEG Oranına Göre Hisse Senedi Yatırımı", "instructor": "Hünkar İvgen"},
    {"id": "2464", "title": "Borsada Fiyat Kazanç Oranına Göre Hisse Senedi Yatırımı", "instructor": "Hünkar İvgen"},
    {"id": "2397", "title": "Firma Değerleme ve Finansal Risk Analizi Platformu Kullanımı", "instructor": "Hünkar İvgen"},
    {"id": "2481", "title": "Finansal Modelleme İle Portföy Oluşturma ve Yönetimi", "instructor": "Tuncay Turşucu"},
    {"id": "1097", "title": "A'dan Z'ye Yatırımcılık", "instructor": "Yaşar Erdinç"},
    {"id": "2449", "title": "Doğru Portföy Yönetimi", "instructor": "Anıl Özekşi"},
]

def parse_vtt(vtt_text):
    """Parse WebVTT content into clean text transcript."""
    lines = vtt_text.strip().split('\n')
    transcript_lines = []
    for line in lines:
        line = line.strip()
        # Skip WEBVTT header, timestamps, and empty lines
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or '-->' in line:
            continue
        # Skip numeric cue identifiers
        if re.match(r'^\d+$', line):
            continue
        # Remove HTML tags if any
        clean = re.sub(r'<[^>]+>', '', line)
        if clean:
            transcript_lines.append(clean)
    return ' '.join(transcript_lines)

async def extract_transcripts():
    if not BORFIN_EMAIL or not BORFIN_PASSWORD:
        print("ERROR: Credentials not found in .env_borfin")
        return

    all_transcripts = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ========== LOGIN ==========
        print("🔑 Logging into Borfin...")
        await page.goto("https://borfin.com/tr/auth/sign-in")
        await page.wait_for_load_state("networkidle")

        # Handle cookie modal
        try:
            cookie_btn = page.locator("button:has-text('Kabul Ediyorum')")
            if await cookie_btn.is_visible(timeout=3000):
                await cookie_btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        await page.wait_for_selector("input[name='email']", state="visible", timeout=10000)
        await page.fill("input[name='email']", BORFIN_EMAIL)
        await page.fill("input[name='password']", BORFIN_PASSWORD)
        await page.click("button:has-text('Giriş yap')")
        
        # Wait for login to complete
        try:
            await page.wait_for_url("**/panel**", timeout=15000)
            print("✅ Login successful!")
        except Exception:
            # Try waiting for any navigation
            await page.wait_for_timeout(5000)
            if "panel" in page.url or "courses" in page.url:
                print("✅ Login successful (alternative check)!")
            else:
                print(f"❌ Login may have failed. Current URL: {page.url}")
                await browser.close()
                return

        # ========== EXTRACT TRANSCRIPTS PER COURSE ==========
        for course_info in COURSE_IDS:
            course_id = course_info["id"]
            course_title = course_info["title"]
            instructor = course_info["instructor"]
            
            print(f"\n📚 Processing: {course_title} ({instructor})")
            
            course_url = f"https://borfin.com/tr/courses/{course_id}/player"
            await page.goto(course_url)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            
            # Extract lesson list from the page
            lessons = await page.evaluate('''() => {
                const items = [];
                // Look for lesson items in the sidebar
                const lessonElements = document.querySelectorAll('[class*="lesson"], [class*="chapter"], [class*="curriculum"] a, [class*="sidebar"] a, .course-content a');
                lessonElements.forEach(el => {
                    const text = el.textContent?.trim();
                    const href = el.getAttribute('href');
                    if (text && text.length > 2) {
                        items.push({title: text, href: href});
                    }
                });
                
                // If no specific lesson elements found, try all clickable items in the course player
                if (items.length === 0) {
                    document.querySelectorAll('button, a').forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.includes('dk') || text?.includes('video')) {
                            items.push({title: text, href: el.getAttribute('href')});
                        }
                    });
                }
                return items;
            }''')
            
            print(f"  Found {len(lessons)} lesson elements")
            
            # Setup VTT interception
            vtt_contents = {}
            
            async def handle_response(response):
                url = response.url
                if '.vtt' in url:
                    try:
                        body = await response.text()
                        vtt_contents[url] = body
                        print(f"  📝 Captured VTT: {url.split('/')[-1]}")
                    except Exception:
                        pass

            page.on("response", handle_response)
            
            # Click through each expandable section and lesson
            # First, expand all chapter/module sections
            chapters = await page.query_selector_all('[class*="chapter"], [class*="section"], [class*="module"], [class*="accordion"]')
            for ch in chapters:
                try:
                    await ch.click()
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
            
            # Now click each lesson to trigger video + VTT load
            lesson_buttons = await page.query_selector_all('[class*="lesson"], [class*="item"]')
            clicked_count = 0
            for btn in lesson_buttons:
                try:
                    btn_text = await btn.text_content()
                    if btn_text and len(btn_text.strip()) > 2:
                        await btn.click()
                        await page.wait_for_timeout(3000)  # Wait for VTT to load
                        clicked_count += 1
                        print(f"  ▶️ Clicked lesson {clicked_count}: {btn_text.strip()[:50]}")
                except Exception:
                    continue
            
            # Remove response listener
            page.remove_listener("response", handle_response)
            
            # Store results for this course
            course_transcripts = []
            for url, vtt_raw in vtt_contents.items():
                clean_text = parse_vtt(vtt_raw)
                subtitle_id = url.split('/')[-1].replace('.vtt', '')
                course_transcripts.append({
                    "subtitle_id": subtitle_id,
                    "vtt_url": url,
                    "raw_vtt": vtt_raw[:200] + "..." if len(vtt_raw) > 200 else vtt_raw,
                    "transcript": clean_text,
                    "word_count": len(clean_text.split())
                })
            
            all_transcripts[course_id] = {
                "title": course_title,
                "instructor": instructor,
                "lessons_found": clicked_count,
                "transcripts_captured": len(course_transcripts),
                "transcripts": course_transcripts
            }
            
            total_words = sum(t["word_count"] for t in course_transcripts)
            print(f"  ✅ Captured {len(course_transcripts)} transcripts ({total_words} words)")

        await browser.close()

    # ========== SAVE RESULTS ==========
    output_file = "borfin_transcripts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "extracted_at": datetime.now().isoformat(),
            "total_courses": len(all_transcripts),
            "courses": all_transcripts
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 All transcripts saved to {output_file}")
    
    # Summary
    total_transcripts = sum(c["transcripts_captured"] for c in all_transcripts.values())
    total_words = sum(
        sum(t["word_count"] for t in c["transcripts"])
        for c in all_transcripts.values()
    )
    print(f"📊 Total: {total_transcripts} transcripts, ~{total_words} words")

if __name__ == "__main__":
    asyncio.run(extract_transcripts())
