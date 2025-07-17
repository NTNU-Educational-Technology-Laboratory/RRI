# config.py

# === AUDIO CONFIG ===
SAMPLERATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.3
SILENCE_DURATION = 1
PRE_BUFFER_DURATION = 0.5  # seconds
INTERRUPTION_VOLUME_THRESHOLD = 70

# === TTS MODEL ===
TTS_MODEL_NAME = "tts_models/en/vctk/vits"   
USE_CUDA = True

# === LLM CONFIG ===
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "mistral"

# === NETWORK CONFIG ===
GPU_SERVER_IP = "192.168.137.217"

# NAO SDK client machine (Python 2.7)
NAO_CLIENT_IP = "192.168.137.59"
NAO_PORT = 5005       # envoie texte → SDK
NAO_FEEDBACK_PORT = 5050     # attend "done" ← NAO

# Reachy client machine
REACHY_CLIENT_IP = "192.168.137.214"
REACHY_PORT = 5007    # envoie .wav → Reachy
REACHY_FEEDBACK_PORT = 5060  # attend "done" ← Reachy

# === ROLES ===
NAO_REAL_IP = "192.168.137.222"   
