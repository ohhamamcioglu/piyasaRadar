import os
import whisper
import json
import subprocess
from datetime import datetime

# Add local venv bin to PATH for ffmpeg
venv_bin = os.path.abspath("venv/bin")
os.environ["PATH"] = venv_bin + os.pathsep + os.environ["PATH"]

def transcribe_local_borfin():
    audio_dir = "borfin_audio"
    output_dir = "borfin_transcripts/2464"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 Initializing Whisper Model (base)...")
    model = whisper.load_model("base")
    
    files = [f for f in os.listdir(audio_dir) if f.startswith("2464") and f.endswith(".webm")]
    files.sort()
    
    for filename in files:
        output_path = os.path.join(output_dir, filename.replace(".webm", ".json"))
        if os.path.exists(output_path):
            print(f"Skipping {filename}, already transcribed.")
            continue
            
        audio_path = os.path.join(audio_dir, filename)
        print(f"🎙️ Transcribing: {filename}...")
        
        try:
            result = model.transcribe(audio_path, language="tr")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"✅ Success: {output_path}")
        except Exception as e:
            print(f"❌ Error transcribing {filename}: {e}")

if __name__ == "__main__":
    transcribe_local_borfin()
