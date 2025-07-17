# RRI Speech Interaction – Robot-to-Robot Communication Prototype

## Project Description

This project is developed as part of a research internship at NTNU.
It explores robot-to-robot interaction (RRI) using speech, language models, and real-time communication between two physical robots: NAO and Reachy.

The system is modular and built for flexible experimentation. The user interface allows configuration of the agents’ behavior, selection of who starts the conversation, and observation of the dialogue in real time.

The entire dialogue logic and coordination are handled on a central GPU server, using an LLM, TTS, and socket-based communication with each robot.

## Main Components

### 1. Web Interface (`app.py`)
Flask app with a SocketIO layer for real-time conversation updates:
- Allows user to define initial contexts for NAO and Reachy
- User can select which agent starts the conversation
- Handles conversation loop between the robots using LLM and TTS
- Uses sockets to:
  - Send plain text to NAO client
  - Send generated audio (WAV) to Reachy client
  - Wait for feedback before proceeding to the next turn

Accessible via browser at `http://localhost:5000/`

### 2. CLI Mode (`mainserver.py`)
Terminal-based launcher to test the robot interaction without the UI:
- Prompts user for the starter and initial topic
- Sends text/audio to the respective robot
- Waits for robot feedback using socket communication
- Handles looped conversation with LLM and TTS

### 3. NAO Client (`nao_client.py`)
- Python 2.7 script using `naoqi` SDK
- Waits for incoming text over socket and uses NAO's native TTS
- Sends a feedback signal when done speaking to unblock the main server

### 4. Reachy Client (`reachyclient.py`)
- Listens on a socket for incoming audio (WAV)
- Uses `simpleaudio` to play the sound on the robot’s speaker
- Sends feedback to the main server after playback

## File Structure (GPU Machine)

```
RRI_SPEECH/
├── app.py
├── mainserver.py
├── config.py
├── requirements.txt
├── setup.py
├── static/
│   └── style.css
├── templates/
│   └── index.html
```

## Dependencies (GPU)

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Required:
- Flask
- Flask-SocketIO
- TTS (by coqui.ai)
- Requests
- uuid
- socket

## Usage

### Launch Web UI:
```bash
python app.py
```

### Launch CLI mode:
```bash
python mainserver.py
```

### On NAO (Python 2.7):
```bash
python nao_client.py
```

### On Reachy:
```bash
python reachyclient.py
```
 