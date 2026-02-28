import queue
import sys
import sounddevice as sd
import json
import os
from vosk import Model, KaldiRecognizer

# ---------------- CONFIG ----------------
WAKE_WORD = "casper"
SAMPLE_RATE = 16000

# -------- Absolute Model Path Fix --------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = r"C:\Users\Prashant Sahay\Downloads\vosk-model-en-in-0.5\vosk-model-en-in-0.5"

print("Loading Vosk model from:", MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model folder not found at {MODEL_PATH}")

# -------- Load Model Once --------
model = Model(MODEL_PATH)

# -------- Audio Queue --------
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def listen_text():
    """
    Capture one complete spoken sentence and return text
    """
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                return text.lower()


def listen_for_wake_word():
    print("\n[Wake Mode] Say wake word...")

    WAKE_VARIANTS = ["casper", "kasper", "caspar", "caspur", "jasper", "spare"]

    while True:
        text = listen_text()
        print("Heard:", text)

        for variant in WAKE_VARIANTS:
            if variant in text:
                print("Wake word detected!")
                return True


def listen_for_question():
    print("\n[Question Mode] Ask now...")

    text = listen_text()

    if len(text.strip()) < 3:
        print("Too short, ignoring.")
        return None

    print("Question captured:", text)
    return text