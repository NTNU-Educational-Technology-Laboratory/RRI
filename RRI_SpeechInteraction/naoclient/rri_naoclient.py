# nao_client.py (Python 2.7)
# -*- coding: utf-8 -*-
import socket
from naoqi import ALProxy

NAO_IP = "192.168.137.222"
NAO_PORT = 9559
LISTEN_PORT = 5005
FEEDBACK_PORT = 5050  # GPU

tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
tts.setVolume(0.3)
tts.setVoice("naoenu")

print("🗣️ NAO is ready to receive text...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", LISTEN_PORT))
server.listen(1)

while True:
    conn, addr = server.accept()
    print("📩 Text received from:", addr)
    data = conn.recv(4096)
    if data:
        message = data.strip()
        print("💬 Saying:", message)
        tts.say(message)

        # Feedback to GPU
        try:
            feedback = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            feedback.connect(("192.168.137.217", FEEDBACK_PORT))
            feedback.sendall(b"done")
            feedback.close()
            print("✅ Feedback sent to GPU")
        except Exception as e:
            print("❌ Feedback error:", e)
    conn.close()