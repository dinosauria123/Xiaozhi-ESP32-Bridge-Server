import os

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000

# LM Studio Configuration
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"  # Usually ignored by LM Studio but required by OpenAI client
SYSTEM_PROMPT = "You are a helpful AI assistant. Please keep your answers short and concise, suitable for voice interaction."

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION = 60  # ms
