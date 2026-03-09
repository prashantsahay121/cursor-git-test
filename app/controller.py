import threading

from app.camera import start_camera, capture_current_frame
from app.speech_to_text import listen_once, detect_language, WAKE_VARIANTS
from app.gemini_client import ask_gemini_with_image
from app.tts import speak
from app.formatter import to_hinglish, split_hindi_response, text_for_tts




END_WORDS = [
    "thank you",
    "thanks",
    "ok",
    "okay",
    "theek hai",
    "thik hai",
    "done",
    "ho gaya",
    "bas",
    "enough",
    "that's all",
    "problem solved"
]



conversation_history = []

def run_assistant():

    camera_thread = threading.Thread(target=start_camera)
    camera_thread.daemon = True
    camera_thread.start()

    print("Assistant started...")


    while True:

        print("\n[Wake Mode] Say wake word...")

        text = listen_once(mode="wake")

        if not text:
            continue

        if any(w in text for w in WAKE_VARIANTS):

            speak("Yes")

            print("\n[Question Mode] Ask now...")

            question = listen_once(mode="question")
            conversation_history.append(f"User: {question}")

            if any(word in question.lower() for word in END_WORDS):

                message = "Glad I could help. If you have another issue, just say Casper."

                print("\nAssistant:\n", message)

                speak(message)

                continue

            if not question:
                continue

            language = detect_language(question)

            print("Capturing frame...")

            image_path = capture_current_frame()

            if not image_path:

                speak("Camera frame not available")
                continue

            print("Calling Gemini...")

            answer = ask_gemini_with_image(
                image_path,
                question,
                language,
                conversation_history
            )
            conversation_history.append(f"Assistant: {answer}")

            if language == "hindi":
                hindi_for_tts, hinglish_for_terminal = split_hindi_response(answer)
                print("\nAnswer:\n")
                print(hinglish_for_terminal)
                raw = hindi_for_tts or answer or ""
                to_speak = text_for_tts(raw)
                speak((to_speak if (to_speak and len(to_speak.strip()) > 2) else raw) or "No response.", language)
            else:
                print("\nAnswer:\n")
                print(answer)
                raw = answer or ""
                to_speak = text_for_tts(raw)
                speak((to_speak if (to_speak and len(to_speak.strip()) > 2) else raw) or "No response.", language)