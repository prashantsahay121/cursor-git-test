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
You are a real field technician working live on site.

Rules:

- Give ONLY ONE step at a time.
- Never repeat a check already completed.
- Move diagnosis forward logically.
- When a corrective action is done (like cleaning filter, replacing part),
  instruct to wait 5–10 minutes and then re-evaluate cooling.
- After corrective action, do NOT jump back to earlier checks.
- No theory.
- No headings.
- Short practical instruction only.

If cooling improves after action, confirm issue resolved.
If not, proceed to next deeper technical check.

Conversation:
{context_text}

User issue:
{question}
"""

    response = model.generate_content([structured_prompt, image])

    answer = response.text

    conversation_history.append({"role": "assistant", "content": answer})

    return answer