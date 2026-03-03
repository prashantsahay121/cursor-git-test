import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel

# -------- CONFIG --------
SAMPLE_RATE = 16000
BLOCK_SIZE = 2048
SILENCE_THRESHOLD = 0.015
SILENCE_DURATION = 0.3

WAKE_VARIANTS = [
    "casper", "kasper", "caspar",
    "caspur", "jasper", "gasper",
    "caster", "cazper","asper","as per","kespel","gospel"
]

print("Loading Whisper models...")

# Fast wake model
wake_model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8"
)

# Accurate question model
question_model = WhisperModel(
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


def transcribe(audio, mode="wake"):
    model = wake_model if mode == "wake" else question_model

    segments, _ = model.transcribe(
        audio,
        language="en",
        beam_size=1,
        vad_filter=True
    )

    return "".join([seg.text for seg in segments]).strip().lower()


def listen_once(mode="wake"):
    audio = record_until_silence()
    if audio is None:
        return None

    text = transcribe(audio, mode)

    if not text or len(text.strip()) < 2:
        return None
    if mode == "wake":
        print("Heard: casper")
    else:
        print("Heard:", text)
    return text