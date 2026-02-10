import edge_tts
import tempfile
import os

class TTSEngine:
    def __init__(self, voice="ja-JP-NanamiNeural"):
        self.voice = voice

    async def generate_audio(self, text, output_file):
        """
        Generate TTS audio and save to output_file.
        """
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
