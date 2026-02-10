from faster_whisper import WhisperModel
import io
import numpy as np

class ASREngine:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        print(f"Loading Whisper model: {model_size} on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_data):
        """
        Transcribe audio data (bytes) to text.
        audio_data: Raw PCM 16kHz mono samples (bytes)
        """
        if not audio_data:
            return ""

        # Convert bytes to numpy array
        # Assuming 16-bit PCM, 16kHz, Mono
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(audio_array, beam_size=5, language="ja")
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
