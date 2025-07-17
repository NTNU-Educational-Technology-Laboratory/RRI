# -*- coding: utf-8 -*-
import socket
from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "192.168.137.222", 9559)
tts.stopAll()
