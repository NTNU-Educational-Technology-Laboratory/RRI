import socket
import config
 

def send_text(ip, port, message, label):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(message.encode('utf-8'))
        s.close()
        print(f"✅ Sent to {label}: {message}")
    except Exception as e:
        print(f"❌ Error sending to {label}:", e)

if __name__ == "__main__":
    message = "Hello from GPU 🧠"

    send_text(config.NAO_CLIENT_IP, config.NAO_PORT, message, "NAO")
    send_text(config.REACHY_CLIENT_IP, config.REACHY_PORT, message, "Reachy")
