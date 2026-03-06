from app.gemini_client import ask_gemini_with_image
from app.tts import speak
from app.camera import start_camera, capture_current_frame
from app.speech_to_text import listen_once, WAKE_VARIANTS
import threading


def run_assistant():

    camera_thread = threading.Thread(target=start_camera)
    camera_thread.daemon = True
    camera_thread.start()

    print("Assistant started...")

    closing_keywords = [
    "thank you",
    "thanks",
    "problem solved",
    "solved",
    "done",
    "it's working",
    "now it is fine",
    "it is cooling now",
    "now it is cooling"
]

    while True:

        print("\n[Wake Mode] Say wake word...")
        text = listen_once(mode="wake")

        if not text:
            continue

        if any(w in text for w in WAKE_VARIANTS):

            speak("Yes?")

            print("\n[Question Mode] Ask now...")
            question = listen_once(mode="question")

            if not question:
                continue

            question_lower = question.lower()

            # ---- CLOSE SESSION CHECK ----
            if any(word in question_lower for word in closing_keywords):
                speak("Great. Glad the issue is resolved. If you need help again, just call me.")
                continue
            # -----------------------------

            print("Capturing frame...")
            image_path = capture_current_frame()

            if not image_path:
                speak("Camera frame not available.")
                continue

            print("Calling Gemini...")
            answer = ask_gemini_with_image(image_path, question)

            print("Answer:", answer)
            speak(answer)