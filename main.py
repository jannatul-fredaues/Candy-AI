from flask import Flask, request, Response
from flask_cors import CORS
from openai import OpenAI
from mode_router import detect_mode, get_system_prompt
from context import trim_conversation
import os
import json

client = OpenAI(api_key=os.getenv("api_key"))

app = Flask(__name__)
CORS(app)

conversation = []

def stream_llm(user_text):
    global conversation

    # Auto-detect mode
    mode = detect_mode(user_text)

    # Initialize system prompt
    if not conversation:
        conversation.append({
            "role": "system",
            "content": get_system_prompt(mode)
        })

    conversation.append({"role": "user", "content": user_text})

    # Trim context
    conversation = trim_conversation(conversation)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        stream=True,
        temperature=0.7,
        max_tokens=500
    )

    full_reply = ""

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            token = delta.content
            full_reply += token
            yield f"data: {json.dumps({'token': token})}\n\n"

    conversation.append({"role": "assistant", "content": full_reply})

    yield f"data: {json.dumps({'done': True, 'mode': mode})}\n\n"


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return Response("Empty input", status=400)

    return Response(
        stream_llm(user_text),
        mimetype="text/event-stream"
    )


@app.route("/reset", methods=["POST"])
def reset():
    conversation.clear()
    return {"status": "conversation reset"}


if __name__ == "__main__":
    print("CALEB backend running on http://127.0.0.1:5000")
    app.run(debug=True, threaded=True)
