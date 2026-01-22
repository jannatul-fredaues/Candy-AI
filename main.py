from flask import Flask, request, Response
from flask_cors import CORS
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

conversation = [
    {
        "role": "system",
        "content": (
            "You are CALEB, a professional, intelligent AI assistant. "
            "You explain clearly, think step by step when needed, "
            "and respond like ChatGPT."
        )
    }
]

def stream_reply(user_text):
    conversation.append({"role": "user", "content": user_text})

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        stream=True,
        temperature=0.7,
        max_tokens=400
    )

    full_reply = ""

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            token = delta.content
            full_reply += token
            yield f"data: {json.dumps({'token': token})}\n\n"

    conversation.append({"role": "assistant", "content": full_reply})
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return Response("Empty message", status=400)

    return Response(
        stream_reply(user_text),
        mimetype="text/event-stream"
    )

if __name__ == "__main__":
    print("CALEB streaming backend running at http://127.0.0.1:5000")
    app.run(debug=True, threaded=True)
