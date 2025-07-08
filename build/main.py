import vosk
import sounddevice as sd
import queue
import json
import pyttsx3
import requests
from datetime import datetime

def ask_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                return result["response"].strip()
            else:
                print(" Ollama replied without 'response':", result)
                return "Sorry, I couldn't understand the local model's output."
        else:
            print(f" Ollama HTTP error {response.status_code}: {response.text}")
            return "Sorry, Ollama returned an error."

    except requests.exceptions.RequestException as e:
        print("🚨 Failed to connect to Ollama:", e)
        return "Sorry, I couldn't connect to the local model."
def get_reply(command):
    command = command.lower()
    if "your name" in command:
        return "My name is Jarvis 1 point O."
    elif "time" in command:
        return "It is " + datetime.now().strftime("%I:%M %p")
    elif "stop" in command or "exit" in command:
        return "Goodbye"
    else:
        return ask_ollama(command)


engine = pyttsx3.init(driverName='nsss')
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

def speak(text):
    print("🗣️ Speaking:", text)
    engine.say(text)
    engine.runAndWait()


q = queue.Queue()
model = vosk.Model("model")

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎤 Listening...")
        rec = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("✅ Final:", result["text"])
                return result["text"]
            else:
                partial = json.loads(rec.PartialResult())
                print("...Partial:", partial.get("partial", ""))

while True:
    command = listen()
    reply = get_reply(command)
    speak(reply)
    if "goodbye" in reply.lower():
        break
