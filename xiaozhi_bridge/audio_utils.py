import struct
import opuslib
import wave
import io
import subprocess
import os

class AudioUtils:
    def __init__(self):
        # Initialize Opus encoder/decoder
        # Sample rate: 16000, Channels: 1
        self.encoder = opuslib.Encoder(16000, 1, opuslib.APPLICATION_VOIP)
        self.decoder = opuslib.Decoder(16000, 1)
        self.pcm_buffer = bytearray()

    def decode_opus(self, opus_data):
        """
        Decode Opus packet to PCM.
        """
        try:
            pcm = self.decoder.decode(opus_data, 960) # 960 samples = 60ms at 16kHz
            return pcm
        except opuslib.OpusError:
            return b""

    def encode_pcm_to_opus(self, pcm_data):
        """
        Encode PCM data (bytes) to Opus packet.
        Frame size must be 960 samples (60ms) for 16kHz.
        """
        try:
            opus_packet = self.encoder.encode(pcm_data, 960)
            return opus_packet
        except opuslib.OpusError as e:
            print(f"Opus encoding error: {e}")
            return b""

    def mp3_to_opus_packets(self, mp3_file):
        """
        Convert MP3 file to a list of Opus packets (bytes).
        1. MP3 -> PCM (via ffmpeg)
        2. PCM -> Opus packets
        """
        # 1. Convert to PCM 16kHz Mono 16-bit
        process = subprocess.Popen(
            ['ffmpeg', '-y', '-i', mp3_file, '-f', 's16le', '-ac', '1', '-ar', '16000', 'pipe:1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        pcm_data, _ = process.communicate()

        packets = []
        frame_size = 960 * 2 # 960 samples * 2 bytes/sample = 1920 bytes
        
        # 2. Chunk PCM and encode
        for i in range(0, len(pcm_data), frame_size):
            chunk = pcm_data[i:i+frame_size]
            if len(chunk) < frame_size:
                # Pad with silence if last chunk is incomplete
                chunk += b'\x00' * (frame_size - len(chunk))
            
            opus_packet = self.encode_pcm_to_opus(chunk)
            if opus_packet:
                packets.append(opus_packet)
                
        return packets
