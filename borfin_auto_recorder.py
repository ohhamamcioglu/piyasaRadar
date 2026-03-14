#!/usr/bin/env python3
"""
Borfin Auto-Recorder 🤖🎥
Logs into Borfin and automatically records course lessons via AudioContext.
Sends audio data to the local borfin_audio_server.py.
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv(".env_borfin")
BORFIN_EMAIL = os.getenv("BORFIN_EMAIL")
BORFIN_PASSWORD = os.getenv("BORFIN_PASSWORD")

async def login_to_borfin(page):
    print("🔑 Logging into Borfin...")
    await page.goto("https://borfin.com/tr/auth/sign-in")
    await page.wait_for_load_state("networkidle")
    
    try:
        cookie_btn = page.locator("button:has-text('Kabul Ediyorum')")
        if await cookie_btn.is_visible(timeout=3000):
            await cookie_btn.click()
    except:
        pass
        
    await page.fill("input[name='email']", BORFIN_EMAIL)
    await page.fill("input[name='password']", BORFIN_PASSWORD)
    await page.click("button:has-text('Giriş yap')")
    
    try:
        await page.wait_for_url("**/panel**", timeout=15000)
        print("✅ Login successful!")
        return True
    except:
        print(f"⚠️ Login might have failed. URL: {page.url}")
        return False

async def record_lesson(page, course_id, lesson_idx, lesson_title):
    print(f"\n▶️ Starting recording for: [{lesson_idx}] {lesson_title}")
    
    # Check if video exists with multiple attempts
    print(f"⌛ Searching for video element for: {lesson_title}...")
    for attempt in range(5):
        try:
            await page.wait_for_selector("video", timeout=10000)
            # Check if video actually has a source or duration
            duration = await page.evaluate("document.querySelector('video').duration")
            if duration and not is_nan(duration):
                print(f"✅ Video found on attempt {attempt+1} (Duration: {duration}s)")
                return True
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Retrying video detection ({attempt+1}/5)...")
            await asyncio.sleep(2)
            
    print("❌ Video element or duration not found after 5 attempts!")
    return False

def is_nan(x):
    import math
    return isinstance(x, float) and math.isnan(x)
        
    # Inject recording script
    js_code = f"""
    () => {{
        window.__recording_done = false;
        window.__recording_result = null;
        
        const video = document.querySelector('video');
        if (!video) {{
            window.__recording_result = 'NO_VIDEO';
            window.__recording_done = true;
            return;
        }}
        
        const duration = video.duration;
        if (!duration || isNaN(duration)) {{
            window.__recording_result = 'NO_DURATION';
            window.__recording_done = true;
            return;
        }}
        
        console.log("Starting Web Audio API capture for " + duration + " seconds...");
        
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)({{sampleRate: 16000}});
        const source = audioCtx.createMediaElementSource(video);
        const dest = audioCtx.createMediaStreamDestination();
        source.connect(dest);
        source.connect(audioCtx.destination);
        
        const rec = new MediaRecorder(dest.stream, {{mimeType: 'audio/webm;codecs=opus'}});
        const chunks = [];
        
        rec.ondataavailable = (e) => {{ if (e.data.size > 0) chunks.push(e.data); }};
        
        rec.onstop = async () => {{
            console.log("Recording stopped. Converting to base64...");
            const blob = new Blob(chunks, {{type: 'audio/webm'}});
            const reader = new FileReader();
            reader.onloadend = async () => {{
                const b64 = reader.result.split(',')[1];
                try {{
                    const resp = await fetch('http://127.0.0.1:9876', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            course_id: '{course_id}',
                            lesson_idx: {lesson_idx},
                            lesson_title: '{lesson_title}',
                            audio_base64: b64,
                            duration: duration
                        }})
                    }});
                    window.__recording_result = 'OK:' + blob.size;
                }} catch(e) {{
                    window.__recording_result = 'SERVER_ERROR:' + e.message;
                }}
                window.__recording_done = true;
            }};
            reader.readAsDataURL(blob);
        }};
        
        video.currentTime = 0;
        video.muted = false;
        video.volume = 1.0;
        video.play();
        rec.start(1000);
        
        const recordMs = (duration + 2) * 1000;
        setTimeout(() => {{
            rec.stop();
            video.pause();
        }}, recordMs);
    }}
    """
    
    await page.evaluate(js_code)
    
    print(f"⏳ Waiting for video to finish naturally... DO NOT INTERRUPT.")
    # Wait until __recording_done is true (max 45 mins)
    await page.wait_for_function("window.__recording_done === true", timeout=45 * 60 * 1000)
    
    result = await page.evaluate("window.__recording_result")
    print(f"✅ Recording finished with result: {result}")
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--autoplay-policy=no-user-gesture-required"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await login_to_borfin(page)
        
        print("📺 Navigating to F/K Course (2464)...")
        await page.goto("https://borfin.com/tr/courses/2464/player")
        await page.wait_for_timeout(5000)
        
        lessons_to_record = [
            (3, "Fiyat Kazanç Oranı Hesaplaması"),
            (4, "F/K Oranı Yaklaşımının Hisse Senetlerinde Uygulanması"),
            (5, "F/K Oranı Temel Stratejileri 1"),
            (6, "F/K Oranı Temel Stratejileri 2"),
            (7, "Kapanış")
        ]
        
        for idx, title in lessons_to_record:
            print(f"\n👉 Clicking on Lesson {idx}: {title}...")
            
            # Click the exact text matching the lesson
            lesson_locator = page.locator(f"text='{title}'").first
            
            try:
                await lesson_locator.scroll_into_view_if_needed(timeout=3000)
                await page.wait_for_timeout(500)
                await lesson_locator.click(timeout=5000, force=True)
            except Exception as e:
                print(f"⚠️ Could not click {title} directly, trying to expand accordions...")
                sections = await page.query_selector_all('[class*="accordion"], [class*="chapter"], [class*="section"]')
                for section in sections:
                    try:
                        await section.click(timeout=1000)
                        await page.wait_for_timeout(300)
                    except:
                        pass
                await lesson_locator.scroll_into_view_if_needed(timeout=3000)
                await lesson_locator.click(timeout=5000, force=True)
                
            await page.wait_for_timeout(4000) # Give it time to load the video
            
            await record_lesson(page, "2464", idx, title)
            await page.wait_for_timeout(2000)
            
        await browser.close()
        print("\n🎉 All requested lessons recorded!")

if __name__ == "__main__":
    asyncio.run(main())
