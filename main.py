from flask import Flask, request, jsonify
from flask_cors import CORS
import pyttsx3
import datetime
import webbrowser
import os

app = Flask(__name__)
CORS(app)

# === Voice Output ===
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    text = data.get("text", "").lower()

    print("Received:", text)

    # Wake word
    if "candy" in text:
        speak("Hi master")
        return jsonify({"reply": "Hi master"})

    # Commands
    if "time" in text:
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {time}")
        return jsonify({"reply": time})

    if "open google" in text:
        speak("Opening Google")
        webbrowser.open("https://google.com")
        return jsonify({"reply": "Opening Google"})

    if "open youtube" in text:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
        return jsonify({"reply": "Opening YouTube"})

    if "shutdown" in text:
        speak("Shutting down system")
        os.system("shutdown /s /t 1")
        return jsonify({"reply": "Shutting down"})

    speak("Sorry master, I did not understand")
    return jsonify({"reply": "Unknown command"})

if __name__ == "__main__":
    app.run(debug=True)
