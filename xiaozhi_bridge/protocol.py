import json
import struct

class Protocol:
    def __init__(self):
        pass

    @staticmethod
    def parse_message(data):
        """
        Parse incoming message from WebSocket.
        Returns:
            - ('json', dict) if it's a JSON text message
            - ('audio', bytes) if it's binary audio data
            - (None, None) if invalid
        """
        if isinstance(data, str):
            try:
                return 'json', json.loads(data)
            except json.JSONDecodeError:
                return None, None
        
        elif isinstance(data, bytes):
            # Check if it has a header or if it's raw opus
            # Protocol v3 might send raw opus or framed opus
            # Simple check: Try to see if it matches header structure
            # But usually for simplicity we assume it's audio if binary
            return 'audio', data
        
        return None, None

    @staticmethod
    def create_hello_response(session_id):
        return json.dumps({
            "type": "hello",
            "transport": "websocket",
            "version": 3,
            "audio_params": {
                "format": "opus",
                "sample_rate": 16000,
                "channels": 1,
                "frame_duration": 60
            },
            "session_id": session_id
        })

    @staticmethod
    def create_tts_start():
        return json.dumps({"type": "tts", "state": "start"})

    @staticmethod
    def create_tts_stop():
        return json.dumps({"type": "tts", "state": "stop"})

    @staticmethod
    def create_tts_sentence_start(text):
        return json.dumps({"type": "tts", "state": "sentence_start", "text": text})

    @staticmethod
    def create_stt_text(text, session_id):
        return json.dumps({
            "type": "stt", 
            "text": text,
            "session_id": session_id
        })
