import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import os

# Configuration
SAMPLE_RATE = 48000  # BirdNET strictly requires 48kHz
CHUNK_DURATION = 3   # 3-second windows
SILENCE_THRESHOLD = 0.015 # Adjust this based on your room's background noise

# A thread-safe queue to hold loud-enough audio chunks
audio_queue = queue.Queue()

def rms_energy(audio_data):
    """Calculates the volume (Root Mean Square energy) of an audio chunk."""
    return np.sqrt(np.mean(np.square(audio_data)))

def audio_callback(indata, frames, time, status):
    """This function is called continuously by sounddevice for every audio block."""
    if status:
        print(f"Audio Error: {status}", flush=True)
    
    audio_data = indata[:, 0]  # Take just the first channel (Mono)
    
    # Simple Voice Activity Detection (VAD)
    if rms_energy(audio_data) > SILENCE_THRESHOLD:
        audio_queue.put(audio_data.copy())
    
def start_listening():
    """Starts the background listening stream."""
    print("🎙️ Ear activated. Listening for birds...")
    
    # Calculate how many frames are in 3 seconds
    block_size = SAMPLE_RATE * CHUNK_DURATION 
    
    # We use a non-blocking InputStream so it runs in the background
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=block_size,
        callback=audio_callback
    )
    stream.start()
    return stream

def save_temp_wav(audio_data, filename="temp_chunk.wav"):
    """Saves the numpy array to a .wav file for BirdNET to analyze."""
    # Convert float32 audio back to 16-bit PCM for saving
    scaled_data = np.int16(audio_data * 32767)
    wav.write(filename, SAMPLE_RATE, scaled_data)
    return filename