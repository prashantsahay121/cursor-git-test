import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel

# ---------------- CONFIG ----------------
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_THRESHOLD = 0.02      # adjust 0.015–0.03 if needed
SILENCE_DURATION = 0.8        # stop after 0.8 sec silence

print("Loading Whisper small.en model...")
model = WhisperModel("small.en", device="cpu", compute_type="int8")

audio_queue = queue.Queue()


# ---------------- AUDIO CALLBACK ----------------
def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


# ---------------- RECORD UNTIL SILENCE ----------------
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

    audio = np.concatenate(recorded, axis=0)
    audio = audio.flatten()

    # normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    return audio


# ---------------- TRANSCRIBE ----------------
def transcribe_audio(audio):
    segments, _ = model.transcribe(
        audio,
        language="en",
        beam_size=1,      # fast
        vad_filter=True
    )

    text = ""
    for segment in segments:
        text += segment.text

    return text.strip().lower()


# ---------------- PUBLIC FUNCTIONS ----------------
def listen_for_wake_word():
    print("\n[Wake Mode] Say wake word...")
    while True:
        audio = record_until_silence()
        text = transcribe_audio(audio)

        if text:
            print("Heard:", text)

        if "casper" in text:
            print("Wake word detected!")
            return True


def listen_for_question():
    print("\n[Question Mode] Ask now...")
    audio = record_until_silence()
    text = transcribe_audio(audio)

    if len(text.strip()) < 3:
        return None

    print("Question:", text)
    return text


# ---------------- TEST MAIN ----------------
if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            question = listen_for_question()
            if question:
                print("Final Output:", question)