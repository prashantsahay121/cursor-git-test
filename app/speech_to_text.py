import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_THRESHOLD = 0.015
SILENCE_DURATION = 0.7

WAKE_VARIANTS = [
    "casper",
    "kasper",
    "caspar",
    "caspur",
    "jasper",
    "gasper",
    "caster",
    "casperr",
    "kesper",
    "cazper",
    "gasper"
]

print("Loading Whisper base.en model...")
model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8"
)

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

def record_until_silence():
    recorded = []
    silence_time = 0
    speech_started = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype="float32",
        callback=callback
    ):
        while True:
            data = audio_queue.get()
            volume = np.abs(data).mean()

            if volume > SILENCE_THRESHOLD:
                speech_started = True
                silence_time = 0
                recorded.append(data)
            elif speech_started:
                silence_time += BLOCK_SIZE / SAMPLE_RATE
                recorded.append(data)

            if speech_started and silence_time > SILENCE_DURATION:
                break

    if not recorded:
        return None

    audio = np.concatenate(recorded, axis=0).flatten()

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    return audio


def transcribe(audio):
    segments, _ = model.transcribe(
        audio,
        language="en",
        beam_size=1,
        vad_filter=True
    )
    return "".join([seg.text for seg in segments]).strip().lower()



def listen_for_wake_word():
    print("\n[Wake Mode] Say wake word...")

    while True:
        audio = record_until_silence()
        if audio is None:
            continue

        text = transcribe(audio)
        print("Heard:", "Casper")

        for variant in WAKE_VARIANTS:
            if variant in text:
                print("Wake word detected!")
                return True


def listen_for_question():
    print("\n[Question Mode] Ask now...")
    audio = record_until_silence()

    if audio is None:
        return None

    text = transcribe(audio)

    if len(text.strip()) < 3:
        return None

    print("Question:", text)
    return text