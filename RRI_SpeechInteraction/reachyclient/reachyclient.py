import socket
import tempfile
import simpleaudio as sa

REACHY_PORT = 5007

print("🔊 Reachy audio server ready")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", REACHY_PORT))
server.listen(1)

while True:
    conn, addr = server.accept()
    print("📥 Incoming audio from:", addr)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with temp_file as f:
        data = conn.recv(4096)
        while data:
            f.write(data)
            data = conn.recv(4096)
    conn.close()

    print("▶️ Playing audio:", temp_file.name)
    wave_obj = sa.WaveObject.from_wave_file(temp_file.name)
    play_obj = wave_obj.play()
    play_obj.wait_done()

    # Feedback to GPU
    try:
        feedback = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        feedback.connect(("192.168.137.217", 5060))
        feedback.sendall(b"done")
        feedback.close()
        print("✅ Sent feedback to GPU")
    except Exception as e:
        print("❌ Error sending feedback:", e)