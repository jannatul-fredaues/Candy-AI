from dotenv import load_dotenv
load_dotenv(override=True)

from groq import Groq
from prompt import MODES
import os

# --------------------
# Groq Client
# --------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DEFAULT_MODE = "general"

CLASSIFIER_PROMPT = """
Classify the user's message into ONE mode only.

Available modes:
- tutor
- coder
- research
- general

Reply with ONLY ONE WORD from the list above.
"""

# --------------------
# Mode Detection
# --------------------
def detect_mode(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=1
        )

        mode = response.choices[0].message.content.strip().lower()

        if mode in MODES:
            return mode

        return DEFAULT_MODE

    except Exception:
        return DEFAULT_MODE


# --------------------
# System Prompt Getter
# --------------------
def get_system_prompt(mode: str) -> str:
    return MODES.get(mode, MODES[DEFAULT_MODE])
