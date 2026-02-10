import asyncio
import websockets
import json
import uuid
import time
import os
import io
import wave
import struct
import math

from config import HOST, PORT, FRAME_DURATION, SAMPLE_RATE
from protocol import Protocol
from asr_engine import ASREngine
from tts_engine import TTSEngine
from llm_client import LLMClient
from audio_utils import AudioUtils

# Threshold for simple energy-based VAD
VAD_THRESHOLD = 500  # Adjust based on mic sensitivity
SILENCE_FRAMES = 10  # 60ms * 10 = 600ms of silence to trigger ASR

class XiaozhiServer:
    def __init__(self):
        self.asr = ASREngine()
        self.tts = TTSEngine()
        self.llm = LLMClient()
        self.audio_utils = AudioUtils()
        
        # Connection state
        self.audio_buffer = bytearray()
        self.silence_counter = 0
        self.is_speaking = False
        self.session_id = str(uuid.uuid4())

    async def handle_connection(self, websocket):
        print(f"New connection from {websocket.remote_address}")
        self.session_id = str(uuid.uuid4())
        
        try:
            async for message in websocket:
                msg_type, data = Protocol.parse_message(message)
                
                if msg_type == 'json':
                    await self.handle_json(websocket, data)
                elif msg_type == 'audio':
                    await self.handle_audio(websocket, data)
                else:
                    print("Unknown message type")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        except Exception as e:
            print(f"Error: {e}")

    async def handle_json(self, websocket, data):
        print(f"Received JSON: {data}")
        msg_type = data.get('type')
        
        if msg_type == 'hello':
            response = Protocol.create_hello_response(self.session_id)
            await websocket.send(response)
            print("Sent Hello response")

    async def handle_audio(self, websocket, opus_data):
        # 1. Decode Opus to PCM
        # Note: In a real robust implementation, we'd handle the 'audio' wrapper 
        # from the device if it's not raw Opus. 
        # But assuming raw Opus or extracting payload...
        # For now, let's try to decode directly.
        
        pcm = self.audio_utils.decode_opus(opus_data)
        if not pcm:
            return

        # 2. VAD & Accumulate
        # Calculate energy (RMS)
        shorts = struct.unpack(f"{len(pcm)//2}h", pcm)
        sum_squares = sum(s**2 for s in shorts)
        rms = math.sqrt(sum_squares / len(shorts))
        
        if rms > VAD_THRESHOLD:
            self.silence_counter = 0
            self.is_speaking = True
            self.audio_buffer.extend(pcm)
        else:
            if self.is_speaking:
                self.silence_counter += 1
                self.audio_buffer.extend(pcm) # Determine if we should keep silence
                
                if self.silence_counter > SILENCE_FRAMES:
                    # Silence detected, trigger ASR
                    await self.process_speech(websocket)
                    self.is_speaking = False
                    self.audio_buffer = bytearray()
                    self.silence_counter = 0

    async def process_speech(self, websocket):
        print("Silence detected, processing speech...")
        
        # 1. Transcribe (ASR)
        # Run in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self.asr.transcribe, bytes(self.audio_buffer))
        
        if not text:
            print("No speech recognized")
            return

        print(f"ASR recognized: {text}")
        
        # Send STT update to client
        await websocket.send(Protocol.create_stt_text(text, self.session_id))

        # 2. Get LLM Response
        print("Asking LLM...")
        llm_response = await self.llm.get_response(text)
        print(f"LLM response: {llm_response}")
        
        # Send TTS Start
        await websocket.send(Protocol.create_tts_start())
        await websocket.send(Protocol.create_tts_sentence_start(llm_response))

        # 3. Generate Audio (TTS)
        # Because we need Opus packets, we generate file then convert
        temp_mp3 = f"resp_{int(time.time())}.mp3"
        await self.tts.generate_audio(llm_response, temp_mp3)
        
        # 4. Stream Audio
        try:
            # Load and convert to Opus packets
            opus_packets = await loop.run_in_executor(None, self.audio_utils.mp3_to_opus_packets, temp_mp3)
            
            for packet in opus_packets:
                await websocket.send(packet)
                # await asyncio.sleep(0.06) # Simulate real-time if needed, but buffering is usually fine
                
            # Send TTS Stop
            await websocket.send(Protocol.create_tts_stop())
            
        except Exception as e:
            print(f"Error streaming TTS: {e}")
        finally:
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)

async def main():
    server = XiaozhiServer()
    async with websockets.serve(server.handle_connection, HOST, PORT):
        print(f"Xiaozhi Bridge Server running on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
