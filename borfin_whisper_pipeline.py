#!/usr/bin/env python3
"""
Borfin Audio Capture + Whisper Pipeline 🎙️🤖
Plays course videos in Chromium and captures audio output via PipeWire,
then transcribes with OpenAI Whisper.

DRM prevents direct DASH download — this approach records the decoded browser audio.
"""
import asyncio
import subprocess
import json
import os
import re
import sys
import time
import signal
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Fix ffmpeg path for Whisper
import imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_path)
os.environ["PATH"] = ffmpeg_dir + ":" + os.environ.get("PATH", "")
# Also create symlink if needed
venv_bin = os.path.join(os.path.dirname(sys.executable))
ffmpeg_link = os.path.join(venv_bin, "ffmpeg")
if not os.path.exists(ffmpeg_link):
    os.symlink(ffmpeg_path, ffmpeg_link)

load_dotenv(".env_borfin")
BORFIN_EMAIL = os.getenv("BORFIN_EMAIL")
BORFIN_PASSWORD = os.getenv("BORFIN_PASSWORD")

AUDIO_DIR = "borfin_audio"
TRANSCRIPT_DIR = "borfin_transcripts"

# Courses to process (without VTT subtitles)
COURSES = {
    "2464": {
        "title": "Borsada Fiyat Kazanç Oranına Göre Hisse Senedi Yatırımı",
        "instructor": "Hünkar İvgen",
    },
    "2481": {
        "title": "Finansal Modelleme İle Portföy Oluşturma ve Yönetimi",
        "instructor": "Tuncay Turşucu",
    },
    "2397": {
        "title": "Firma Değerleme ve Finansal Risk Analizi Platformu Kullanımı",
        "instructor": "Hünkar İvgen",
    },
    "1097": {
        "title": "A'dan Z'ye Yatırımcılık",
        "instructor": "Yaşar Erdinç",
    }
}

# Pre-load Whisper model once
_whisper_model = None
def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print("  📦 Loading Whisper model (base)...")
        _whisper_model = whisper.load_model("base")
    return _whisper_model

async def login_to_borfin(page):
    """Login to Borfin with retry logic."""
    print("🔑 Logging into Borfin...")
    
    for attempt in range(3):
        await page.goto("https://borfin.com/tr/auth/sign-in")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # Handle cookie modal
        try:
            cookie_btn = page.locator("button:has-text('Kabul Ediyorum')")
            if await cookie_btn.is_visible(timeout=3000):
                await cookie_btn.click()
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Fill credentials
        try:
            await page.wait_for_selector("input[name='email']", state="visible", timeout=10000)
            await page.fill("input[name='email']", BORFIN_EMAIL)
            await page.fill("input[name='password']", BORFIN_PASSWORD)
            await page.wait_for_timeout(500)
            
            # Click login
            await page.click("button[type='submit']")
            await page.wait_for_timeout(3000)
            
            # Check if login succeeded
            current_url = page.url
            if "panel" in current_url or "courses" in current_url or "dashboard" in current_url:
                print("✅ Login successful!")
                return True
            
            # Try alternative login button
            try:
                await page.click("button:has-text('Giriş')")
                await page.wait_for_timeout(5000)
            except:
                pass
            
            current_url = page.url
            if "auth" not in current_url or "sign-in" not in current_url:
                print(f"✅ Login successful! (URL: {current_url})")
                return True
            
            print(f"  ⚠️  Attempt {attempt+1} failed, URL: {current_url}")
        except Exception as e:
            print(f"  ❌ Attempt {attempt+1} error: {e}")
    
    print("❌ Login failed after 3 attempts")
    return False

async def get_lesson_list(page):
    """Extract lesson list from course player page."""
    await page.wait_for_timeout(2000)
    
    # First expand all accordion sections
    while True:
        collapsed = await page.query_selector_all('[class*="accordion"]:not([class*="open"]):not([class*="active"]):not([class*="expanded"])')
        if not collapsed:
            break
        clicked = False
        for el in collapsed:
            try:
                await el.click()
                await page.wait_for_timeout(300)
                clicked = True
            except:
                pass
        if not clicked:
            break
    
    await page.wait_for_timeout(1000)
    
    # Extract lessons using JavaScript
    lessons = await page.evaluate("""() => {
        const results = [];
        // Find all clickable lesson items
        const allElements = document.querySelectorAll('button, a, [role="button"], li');
        for (const el of allElements) {
            const text = el.textContent?.trim() || '';
            // Filter for actual lessons (have duration like "23 dk" or "dk" or are numbered)
            if (text.includes('dk') || text.includes('video') || text.includes('Video')) {
                // Clean up the title - remove duration info
                let title = text.replace(/\\d+\\s*dk/g, '').replace(/\\d+\\s*video/gi, '').trim();
                // Remove extra whitespace
                title = title.replace(/\\s+/g, ' ').trim();
                if (title.length > 3 && title.length < 200) {
                    // Get a unique selector for this element
                    const rect = el.getBoundingClientRect();
                    results.push({
                        title: title,
                        y: rect.top + rect.height / 2,
                        x: rect.left + rect.width / 2,
                        visible: rect.height > 0
                    });
                }
            }
        }
        return results;
    }""")
    
    # Filter out duplicates and non-visible items
    seen = set()
    unique_lessons = []
    for l in lessons:
        if l["title"] not in seen and l["visible"]:
            seen.add(l["title"])
            unique_lessons.append(l)
    
    return unique_lessons

async def capture_lesson_audio(page, lesson_title, course_id, lesson_idx):
    """Capture audio from a playing video lesson using PipeWire pw-record."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    safe_title = re.sub(r'[^\w\s-]', '', lesson_title).strip().replace(' ', '_')[:50]
    wav_path = os.path.join(AUDIO_DIR, f"{course_id}_{lesson_idx:03d}_{safe_title}.wav")
    
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 50000:
        print(f"    ⏭️  Already captured: {wav_path}")
        return wav_path

    # Get video duration
    duration = 0
    for _ in range(5):
        duration = await page.evaluate("""() => {
            const video = document.querySelector('video');
            return video ? video.duration : 0;
        }""")
        if duration and duration > 0:
            break
        await page.wait_for_timeout(1000)
    
    if not duration or duration <= 0 or duration != duration:  # NaN check
        print(f"    ⚠️  Could not determine video duration, skipping")
        return None
    
    print(f"    ⏱️  Video duration: {duration:.0f}s ({duration/60:.1f} min)")
    
    # Start pw-record in background
    rec_process = subprocess.Popen(
        ["pw-record", "--format", "s16", "--rate", "16000", "--channels", "1", wav_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    await page.wait_for_timeout(500)  # Let recorder initialize
    
    try:
        # Ensure video plays from start
        await page.evaluate("""() => {
            const video = document.querySelector('video');
            if (video) {
                video.currentTime = 0;
                video.muted = false;
                video.volume = 1.0;
                video.play();
            }
        }""")
        
        # Wait for the video to finish
        wait_time = int(duration) + 3
        print(f"    🎵 Recording audio for {wait_time}s...")
        
        for elapsed in range(0, wait_time, 30):
            remaining = min(30, wait_time - elapsed)
            await page.wait_for_timeout(remaining * 1000)
            if elapsed > 0 and elapsed % 60 == 0:
                print(f"    ⏳ {elapsed}s / {wait_time}s ({elapsed*100//wait_time}%)")
        
        # Pause video
        await page.evaluate("document.querySelector('video')?.pause()")
        
    finally:
        # Stop recording gracefully
        try:
            rec_process.send_signal(signal.SIGINT)
            rec_process.wait(timeout=5)
        except:
            rec_process.kill()
    
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 10000:
        size_mb = os.path.getsize(wav_path) / (1024 * 1024)
        print(f"    📥 Captured: {size_mb:.1f} MB")
        return wav_path
    else:
        print(f"    ❌ Recording failed or empty")
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return None

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper."""
    model = get_whisper_model()
    print(f"    🎙️ Transcribing...")
    result = model.transcribe(audio_path, language="tr", fp16=False)
    transcript = result["text"].strip()
    word_count = len(transcript.split())
    print(f"    ✅ {word_count} words transcribed")
    return transcript

async def process_course(page, course_id, course_info, all_data):
    """Process a single course: navigate, extract lessons, capture audio, transcribe."""
    print(f"\n{'='*60}")
    print(f"📚 {course_info['title']} ({course_info['instructor']})")
    print(f"{'='*60}")
    
    course_url = f"https://borfin.com/tr/courses/{course_id}/player"
    await page.goto(course_url)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)
    
    # Get lesson list
    lessons = await get_lesson_list(page)
    print(f"  📋 Found {len(lessons)} lessons")
    
    if not lessons:
        print("  ⚠️  No lessons found, skipping course")
        return
    
    course_result = {
        "title": course_info["title"],
        "instructor": course_info["instructor"],
        "lessons": [],
        "source": "whisper_ai"
    }
    
    for i, lesson in enumerate(lessons, 1):
        print(f"\n  [{i}/{len(lessons)}] {lesson['title']}")
        
        # Click the lesson (scroll to it and click)
        try:
            await page.evaluate(f"window.scrollTo(0, {max(0, lesson['y'] - 300)})")
            await page.wait_for_timeout(300)
            await page.mouse.click(lesson["x"], lesson["y"])
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"    ❌ Could not click lesson: {e}")
            continue
        
        # Capture audio
        wav_path = await capture_lesson_audio(page, lesson["title"], course_id, i)
        
        if wav_path:
            try:
                transcript = transcribe_audio(wav_path)
                course_result["lessons"].append({
                    "title": lesson["title"],
                    "transcript": transcript,
                    "word_count": len(transcript.split()),
                    "source": "whisper_base"
                })
            except Exception as e:
                print(f"    ❌ Whisper error: {e}")
                course_result["lessons"].append({
                    "title": lesson["title"],
                    "transcript": "",
                    "word_count": 0,
                    "error": str(e)
                })
        else:
            course_result["lessons"].append({
                "title": lesson["title"],
                "transcript": "",
                "word_count": 0,
                "error": "Audio capture failed"
            })
    
    total_words = sum(l["word_count"] for l in course_result["lessons"])
    print(f"\n  📊 Course total: {total_words} words from {len(course_result['lessons'])} lessons")
    
    all_data["courses"][course_id] = course_result
    
    # Save after each course
    all_data["extracted_at"] = datetime.now().isoformat()
    with open("borfin_transcripts.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved to borfin_transcripts.json")

async def main():
    target_course = None
    if len(sys.argv) > 2 and sys.argv[1] == "--course":
        target_course = sys.argv[2]
    
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    
    # Load existing transcripts
    transcript_file = "borfin_transcripts.json"
    if os.path.exists(transcript_file):
        with open(transcript_file, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = {"extracted_at": "", "courses": {}}
    
    courses_to_process = COURSES
    if target_course:
        if target_course not in COURSES:
            print(f"Course {target_course} not found. Available: {list(COURSES.keys())}")
            return
        courses_to_process = {target_course: COURSES[target_course]}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--autoplay-policy=no-user-gesture-required", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Login
        logged_in = await login_to_borfin(page)
        if not logged_in:
            # Try navigating directly — maybe cookies from the browser subagent session work
            await page.goto("https://borfin.com/tr/panel/courses")
            await page.wait_for_timeout(3000)
            if "auth" in page.url:
                print("❌ Cannot proceed without login")
                await browser.close()
                return
        
        # Process courses
        for course_id, course_info in courses_to_process.items():
            await process_course(page, course_id, course_info, all_data)
        
        await browser.close()
    
    # Grand total
    total_words = sum(
        sum(l["word_count"] for l in c["lessons"])
        for c in all_data["courses"].values()
    )
    total_lessons = sum(len(c["lessons"]) for c in all_data["courses"].values())
    print(f"\n🎉 Grand Total: {total_lessons} lessons, ~{total_words} words across {len(all_data['courses'])} courses")

if __name__ == "__main__":
    asyncio.run(main())
