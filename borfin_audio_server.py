#!/usr/bin/env python3
"""
Borfin Audio Receiver Server 🔊📡
Local HTTP server that receives audio chunks from the browser via POST requests.
The browser JavaScript (injected via AudioContext) sends recorded audio data here.
"""
import http.server
import json
import os
import base64
import threading
from datetime import datetime

AUDIO_DIR = "borfin_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

received_files = []

class AudioHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            course_id = data.get("course_id", "unknown")
            lesson_idx = data.get("lesson_idx", 0)
            lesson_title = data.get("lesson_title", "unknown")
            audio_b64 = data.get("audio_base64", "")
            duration = data.get("duration", 0)
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_b64)
            
            # Save to file
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in lesson_title).strip().replace(' ', '_')[:50]
            filename = f"{course_id}_{lesson_idx:03d}_{safe_title}.webm"
            filepath = os.path.join(AUDIO_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            
            size_kb = len(audio_bytes) / 1024
            received_files.append(filepath)
            print(f"✅ Saved: {filename} ({size_kb:.1f} KB, {duration:.0f}s)")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "file": filepath}).encode())
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress access logs

def start_server(port=9876):
    server = http.server.HTTPServer(('127.0.0.1', port), AudioHandler)
    print(f"🔊 Audio Receiver listening on http://127.0.0.1:{port}")
    print(f"📁 Saving to: {os.path.abspath(AUDIO_DIR)}/")
    print(f"⏳ Waiting for audio data from browser...")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
