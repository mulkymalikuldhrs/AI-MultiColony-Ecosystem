"""👁️ RecognitionAgent – unified multimodal recognition (image, audio, text).
Note: For demo, uses Pillow + pytesseract (OCR) for image text, speech_recognition for audio.
Install extras: pip install pillow pytesseract speechrecognition pyaudio --no-cache-dir
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

class RecognitionAgent:
    status = "ready"
    capabilities = ["image_recognition", "audio_transcribe", "text_entity"]

    def recognize_image(self, image_path: str) -> Dict[str, Any]:
        if not (Image and pytesseract):
            return {"error": "PIL/pytesseract not installed"}
        if not Path(image_path).exists():
            return {"error": "file-not-found"}
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return {"text": text.strip()}

    def recognize_audio(self, audio_path: str) -> Dict[str, Any]:
        if not sr:
            return {"error": "speech_recognition not installed"}
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except Exception as e:
            return {"error": str(e)}
        return {"text": text}

    def recognize_text(self, text: str) -> Dict[str, Any]:
        # simple placeholder entity extraction (keywords)
        keywords = [w for w in text.split() if w.istitle()]
        return {"keywords": keywords}

def recognition_agent():
    return RecognitionAgent()