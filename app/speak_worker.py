"""
Run in subprocess: reads text from file and speaks once. Avoids pyttsx3 engine
getting stuck on Windows when used repeatedly in the main process.
"""
import sys
import os
import pyttsx3

def main():
    if len(sys.argv) < 2:
        return
    path = sys.argv[1]
    language = (sys.argv[2] or "").strip().lower() if len(sys.argv) > 2 else "english"
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    voice_id = None
    want_hindi = language == "hindi"
    for v in voices:
        name = v.name.lower()
        # When user spoke Hindi, use Hindi voice (Hemant/Kalpana) so full sentence is spoken in Hindi
        if want_hindi and ("hindi" in name or "hemant" in name or "kalpana" in name):
            voice_id = v.id
            break
        if not want_hindi and "david" in name:
            voice_id = v.id
            break
        if "hemant" in name:
            voice_id = v.id
        if "david" in name and voice_id is None:
            voice_id = v.id
        elif ("male" in name or "boy" in name) and voice_id is None:
            voice_id = v.id
    if voice_id is None and voices:
        voice_id = voices[0].id
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        sys.stderr.write(str(e) + "\n")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
