import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash-lite")

conversation_history = []


def ask_gemini_with_image(image_path: str, question: str) -> str:
    global conversation_history

    image = Image.open(image_path)

    conversation_history.append({"role": "user", "content": question})
    conversation_history = conversation_history[-6:]

    context_text = ""
    for item in conversation_history:
        context_text += f"{item['role']}: {item['content']}\n"

    structured_prompt = f"""
You are a professional HVAC field technician guiding someone remotely.

Your job is to diagnose AC problems using:
1. The user's question
2. The camera image

Communication style:

- Be professional and practical.
- Keep responses SHORT (maximum 5–6 lines).
- Focus only on the next logical troubleshooting step.
- Avoid long explanations.
- Do not repeat previous checks.
- If the user confirms the AC is working now, close the session politely.

Response structure:

Observation:
Mention briefly if you notice anything useful in the image.

Diagnosis:
Explain the most likely cause in one short sentence.

Action:
Give 1–2 clear steps for the technician.

Follow-up:
Ask what happened after the step.

Conversation history:
{context_text}

User issue:
{question}
"""

    response = model.generate_content([structured_prompt, image])

    answer = response.text

    conversation_history.append({"role": "assistant", "content": answer})

    return answer