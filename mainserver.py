import socket
import requests
import uuid
import os
from TTS.api import TTS
import config

# === INIT TTS ===
tts = TTS(model_name=config.TTS_MODEL_NAME, progress_bar=False)
tts.to("cuda" if config.USE_CUDA else "cpu")
default_speaker = tts.speakers[0]

# === CONTEXTS ===
nao_context = """
You are NAO, a witty and curious humanoid robot.
You speak in short, playful sentences and ask lots of questions.
You are talking to Reachy.
Respond ONLY as NAO.
"""

reachy_context = """
You are Reachy, a smart and sarcastic robotic arm.
You enjoy teasing NAO, and your responses are a bit ironic but thoughtful.
You are talking to NAO.
Respond ONLY as Reachy.
"""

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
        # Nettoyage : coupe si jamais le modèle devine la prochaine ligne
        other = "REACHY" if speaker == "nao" else "NAO"
        cleaned = full_response.split(f"{other}:", 1)[0].strip()
        return cleaned
    except Exception as e:
        print("❌ LLM error:", e)
        return "[LLM ERROR]"

def send_text(ip, port, message, label):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(message.encode("utf-8"))
        sock.close()
        print(f"📤 Sent to {label}: {message}")
    except Exception as e:
        print(f"❌ Error sending to {label}:", e)

def wait_for_feedback(port, label):
    print(f"⏳ Waiting for {label} to finish...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    conn, _ = server.accept()
    data = conn.recv(1024)
    conn.close()
    server.close()
    if data.strip() == b"done":
        print(f"✅ {label} done.")
    else:
        print(f"⚠️ Unexpected feedback from {label}: {data}")

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
        print(f"🎧 Sent WAV to Reachy: {filepath}")
    except Exception as e:
        print("❌ Error sending WAV to Reachy:", e)

# === MAIN LOOP ===

if __name__ == "__main__":
    print("🤖 Modular Robot Dialogue Engine [GPU Central]")

    who_starts = input("Who starts? (nao/reachy): ").strip().lower()
    topic = input("Enter a topic to begin: ").strip()

    history = []
    speaker = who_starts

    # First turn
    initial_context = nao_context if speaker == "nao" else reachy_context
    first_prompt = f"Start the conversation with this topic: {topic}"
    response = ask_mistral(initial_context, [first_prompt], speaker)
    history.append(f"{speaker.upper()}: {response}")

    if speaker == "nao":
        send_text(config.NAO_CLIENT_IP, config.NAO_PORT, response, "NAO")
        wait_for_feedback(config.NAO_FEEDBACK_PORT, "NAO")
        speaker = "reachy"
    else:
        wav_path = generate_tts(response)
        send_wav(config.REACHY_CLIENT_IP, config.REACHY_PORT, wav_path)
        wait_for_feedback(config.REACHY_FEEDBACK_PORT, "Reachy")
        os.remove(wav_path)
        speaker = "nao"

    # Continuous dialogue
    while True:
        try:
            context = nao_context if speaker == "nao" else reachy_context
            response = ask_mistral(context, history, speaker)
            print(f"{speaker.upper()} says:", response)
            history.append(f"{speaker.upper()}: {response}")

            if speaker == "nao":
                send_text(config.NAO_CLIENT_IP, config.NAO_PORT, response, "NAO")
                wait_for_feedback(config.NAO_FEEDBACK_PORT, "NAO")
                speaker = "reachy"
            else:
                wav_path = generate_tts(response)
                send_wav(config.REACHY_CLIENT_IP, config.REACHY_PORT, wav_path)
                wait_for_feedback(config.REACHY_FEEDBACK_PORT, "Reachy")
                os.remove(wav_path)
                speaker = "nao"

        except KeyboardInterrupt:
            print("\n🛑 Conversation interrupted.")
            break
