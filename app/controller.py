from app.gemini_client import ask_gemini_with_image
from app.tts import speak
from app.camera import start_camera, capture_current_frame
from app.speech_to_text import listen_for_wake_word, listen_for_question
import threading


def run_assistant():

    camera_thread = threading.Thread(target=start_camera)
    camera_thread.daemon = True
    camera_thread.start()

    print("Assistant started...")

    while True:
        if listen_for_wake_word():

            speak("Yes, what is your question?")

            question = listen_for_question()

            if not question:
                continue

            print("Capturing frame...")
            image_path = capture_current_frame()

            if not image_path:
                print("No frame available")
                speak("Camera frame not available.")
                continue

            print("Calling Gemini...")
            answer = ask_gemini_with_image(image_path, question)

            print("Answer:", answer)
            speak(answer)