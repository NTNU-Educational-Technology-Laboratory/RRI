from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import socket
import requests
import uuid
import os
from TTS.api import TTS
import config
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

# === INIT TTS ===
tts = TTS(model_name=config.TTS_MODEL_NAME, progress_bar=False)
tts.to("cuda" if config.USE_CUDA else "cpu")
default_speaker = tts.speakers[0]

# === CONTEXTS ===
nao_context = """You are NAO, a witty and curious humanoid robot.
You speak in short, playful sentences and ask lots of questions.
You are talking to Reachy.
Respond ONLY as NAO."""

reachy_context = """You are Reachy, a smart and sarcastic robotic arm.
You enjoy teasing NAO, and your responses are a bit ironic but thoughtful.
You are talking to NAO.
Respond ONLY as Reachy."""

# === HELPERS ===
def ask_mistral(context, history, speaker):
    prompt = context + "\n" + "\n".join(history[-6:]) + f"\n{speaker.upper()}:"
    try:
        res = requests.post(config.OLLAMA_URL, json={
            "model": config.LLM_MODEL,
            "prompt": prompt,
            "stream": False
        })
        res.raise_for_status()
        full_response = res.json()["response"].strip()
        other = "REACHY" if speaker == "nao" else "NAO"
        return full_response.split(f"{other}:", 1)[0].strip()
    except Exception as e:
        return f"[LLM ERROR] {e}"

def send_text(ip, port, message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(message.encode("utf-8"))
        sock.close()
    except Exception as e:
        print(f"❌ Send text error: {e}")

def wait_for_feedback(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(1)
        conn, _ = sock.accept()
        data = conn.recv(1024)
        conn.close()
        sock.close()
    except Exception as e:
        print(f"⚠️ Feedback error: {e}")

def generate_tts(text):
    filename = f"reachy_{uuid.uuid4().hex}.wav"
    tts.tts_to_file(text=text, file_path=filename, speaker=default_speaker)
    return filename

def send_wav(ip, port, filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(data)
        sock.close()
    except Exception as e:
        print(f"❌ Send WAV error: {e}")

# === CONVERSATION THREAD ===
def conversation_loop(start_speaker, topic):
    history = []
    speaker = start_speaker
    context = nao_context if speaker == "nao" else reachy_context
    first_prompt = f"Start the conversation with this topic: {topic}"
    response = ask_mistral(context, [first_prompt], speaker)
    history.append(f"{speaker.upper()}: {response}")
    socketio.emit('new_message', {'speaker': speaker, 'text': response})

    if speaker == "nao":
        send_text(config.NAO_CLIENT_IP, config.NAO_PORT, response)
        wait_for_feedback(config.NAO_FEEDBACK_PORT)
        speaker = "reachy"
    else:
        wav_path = generate_tts(response)
        send_wav(config.REACHY_CLIENT_IP, config.REACHY_PORT, wav_path)
        wait_for_feedback(config.REACHY_FEEDBACK_PORT)
        os.remove(wav_path)
        speaker = "nao"

    # Continuous loop
    while True:
        context = nao_context if speaker == "nao" else reachy_context
        response = ask_mistral(context, history, speaker)
        history.append(f"{speaker.upper()}: {response}")
        socketio.emit('new_message', {'speaker': speaker, 'text': response})

        if speaker == "nao":
            send_text(config.NAO_CLIENT_IP, config.NAO_PORT, response)
            wait_for_feedback(config.NAO_FEEDBACK_PORT)
            speaker = "reachy"
        else:
            wav_path = generate_tts(response)
            send_wav(config.REACHY_CLIENT_IP, config.REACHY_PORT, wav_path)
            wait_for_feedback(config.REACHY_FEEDBACK_PORT)
            os.remove(wav_path)
            speaker = "nao"
        time.sleep(0.5)

# === ROUTES ===
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start')
def start_chat(data):
    global nao_context, reachy_context, history
    nao_context = data.get('nao_context', nao_context)
    reachy_context = data.get('reachy_context', reachy_context)
    history = []  # Reset previous conversation
    start_speaker = data.get('who', 'nao')
    topic = data.get('topic', 'space exploration')
    threading.Thread(target=conversation_loop, args=(start_speaker, topic), daemon=True).start()



if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
