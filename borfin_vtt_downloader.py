#!/usr/bin/env python3
"""
Borfin VTT Downloader — Downloads and parses WebVTT subtitle files. 📥📝
"""
import requests
import json
import re
import os

# VTT URLs extracted by the browser subagent
VTT_DATA = {
    "2466": {
        "title": "PEG Oranına Göre Hisse Senedi Yatırımı",
        "instructor": "Hünkar İvgen",
        "lessons": [
            {"title": "Giriş", "vtt": "https://files.borfin.com/public/subtitle/775366a9b94f485eb0742163d23501f2/775366a9b94f485eb0742163d23501f2.vtt"},
            {"title": "PEG Oranı Nedir", "vtt": "https://files.borfin.com/public/subtitle/b264eebc561641dfb4d2fa02615b9d51/b264eebc561641dfb4d2fa02615b9d51.vtt"},
            {"title": "PEG Oranının Avantajları", "vtt": "https://files.borfin.com/public/subtitle/84dfbd3d3e2a421ca050d9be43daa70e/84dfbd3d3e2a421ca050d9be43daa70e.vtt"},
            {"title": "PEG Oranı Uygulamaları 1", "vtt": "https://files.borfin.com/public/subtitle/835b05781bd049c2b4fa952586c46c5b/835b05781bd049c2b4fa952586c46c5b.vtt"},
            {"title": "PEG Oranı Uygulamaları 2", "vtt": "https://files.borfin.com/public/subtitle/df5ec85bd94444ed9c4e9902621ecddf/df5ec85bd94444ed9c4e9902621ecddf.vtt"},
            {"title": "PEG Oranı Uygulamaları 3", "vtt": "https://files.borfin.com/public/subtitle/4713d2732aa842f4ae3e6ad2cf5e8aa3/4713d2732aa842f4ae3e6ad2cf5e8aa3.vtt"},
            {"title": "Kapanış", "vtt": "https://files.borfin.com/public/subtitle/6053d3a249254c6da8bc8edda5323850/6053d3a249254c6da8bc8edda5323850.vtt"},
        ]
    },
    "2449": {
        "title": "Doğru Portföy Yönetimi",
        "instructor": "Anıl Özekşi",
        "lessons": [
            {"title": "Portföy Seçimi Giriş", "vtt": "https://files.borfin.com/public/subtitle/13758afe5252465899ada7d33addaf41/13758afe5252465899ada7d33addaf41.vtt"},
            {"title": "Yanlış Seçimler", "vtt": "https://files.borfin.com/public/subtitle/673321c00ce84462af50b5361f1231dc/673321c00ce84462af50b5361f1231dc.vtt"},
            {"title": "Portföy Aday Listeleri", "vtt": "https://files.borfin.com/public/subtitle/b035dd01532b40198d3c07be3ad427cb/b035dd01532b40198d3c07be3ad427cb.vtt"},
            {"title": "Portföy Seçimi Sonuç", "vtt": "https://files.borfin.com/public/subtitle/aaa457d448ef473aac547a1846d97da2/aaa457d448ef473aac547a1846d97da2.vtt"},
            {"title": "Portföy Seçimi Gelişme", "vtt": "https://files.borfin.com/public/subtitle/506e55c8f2e44e0881ae87c7b22f931a/506e55c8f2e44e0881ae87c7b22f931a.vtt"},
        ]
    }
}

def parse_vtt(vtt_text):
    """Parse WebVTT content into clean text transcript."""
    lines = vtt_text.strip().split('\n')
    transcript_lines = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or '-->' in line:
            continue
        if re.match(r'^\d+$', line):
            continue
        clean = re.sub(r'<[^>]+>', '', line)
        if clean and clean not in seen:
            transcript_lines.append(clean)
            seen.add(clean)
    return ' '.join(transcript_lines)

def download_all():
    os.makedirs("borfin_transcripts", exist_ok=True)
    all_results = {}
    
    for course_id, course_data in VTT_DATA.items():
        print(f"\n📚 {course_data['title']} ({course_data['instructor']})")
        course_result = {
            "title": course_data["title"],
            "instructor": course_data["instructor"],
            "lessons": []
        }
        
        for lesson in course_data["lessons"]:
            print(f"  📥 Downloading: {lesson['title']}...")
            try:
                resp = requests.get(lesson["vtt"], timeout=15)
                if resp.status_code == 200:
                    vtt_raw = resp.text
                    transcript = parse_vtt(vtt_raw)
                    
                    # Save individual VTT file
                    safe_title = re.sub(r'[^\w\s-]', '', lesson["title"]).strip().replace(' ', '_')
                    vtt_path = f"borfin_transcripts/{course_id}_{safe_title}.vtt"
                    with open(vtt_path, "w", encoding="utf-8") as f:
                        f.write(vtt_raw)
                    
                    course_result["lessons"].append({
                        "title": lesson["title"],
                        "transcript": transcript,
                        "word_count": len(transcript.split()),
                        "vtt_file": vtt_path
                    })
                    print(f"    ✅ {len(transcript.split())} words captured")
                else:
                    print(f"    ❌ HTTP {resp.status_code}")
                    course_result["lessons"].append({
                        "title": lesson["title"],
                        "transcript": "",
                        "word_count": 0,
                        "error": f"HTTP {resp.status_code}"
                    })
            except Exception as e:
                print(f"    ❌ Error: {e}")
                course_result["lessons"].append({
                    "title": lesson["title"],
                    "transcript": "",
                    "word_count": 0,
                    "error": str(e)
                })
        
        total_words = sum(l["word_count"] for l in course_result["lessons"])
        print(f"  📊 Total: {total_words} words from {len(course_result['lessons'])} lessons")
        all_results[course_id] = course_result
    
    # Save master JSON
    output = {
        "extracted_at": __import__('datetime').datetime.now().isoformat(),
        "courses": all_results
    }
    with open("borfin_transcripts.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 All transcripts saved to borfin_transcripts.json and borfin_transcripts/ folder")

if __name__ == "__main__":
    download_all()
