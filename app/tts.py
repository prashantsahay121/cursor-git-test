"""
TTS: run every utterance in a subprocess so each speak() uses a fresh engine.
Reliable on Windows (avoids SAPI/pyttsx3 stuck state in main process).
"""
import sys
import os
import subprocess
import tempfile

_worker = os.path.abspath(os.path.join(os.path.dirname(__file__), "speak_worker.py"))


def speak(text, language="english"):
    text = (text or "").strip()
    if not text:
        return

    if not os.path.isfile(_worker):
        _speak_inprocess(text)
        return

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(text)
            path = f.name
        try:
            subprocess.run(
                [sys.executable, _worker, path, language],
                capture_output=True,
                timeout=90,
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass
    except Exception:
        _speak_inprocess(text, language)


def _speak_inprocess(text, language="english"):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        want_hindi = (language or "").lower() == "hindi"
        voice_id = None
        for v in engine.getProperty("voices"):
            if want_hindi and ("hindi" in v.name.lower() or "hemant" in v.name.lower() or "kalpana" in v.name.lower()):
                voice_id = v.id
                break
            if not want_hindi and "david" in v.name.lower():
                voice_id = v.id
                break
            if voice_id is None and ("hemant" in v.name.lower() or "david" in v.name.lower()):
                voice_id = v.id
        if voice_id:
            engine.setProperty("voice", voice_id)
        engine.say(str(text).strip())
        engine.runAndWait()
        del engine
    except Exception as e:
        print("TTS error:", e)
