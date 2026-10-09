import os
import urllib.request
import zipfile
import subprocess
import winsound 

PIPER_ZIP_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
VOICE_ONNX_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
VOICE_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"

def setup_voice():
    """Downloads the Piper standalone Windows executable and the Voice Model."""
    if not os.path.exists("piper/piper.exe"):
        print("📥 Downloading Piper TTS Engine (15 MB)...")
        urllib.request.urlretrieve(PIPER_ZIP_URL, "piper.zip")
        with zipfile.ZipFile("piper.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove("piper.zip")
        print("✅ Piper Engine ready.")
        
    if not os.path.exists("voice.onnx"):
        print("📥 Downloading Voice Model...")
        urllib.request.urlretrieve(VOICE_ONNX_URL, "voice.onnx")
        urllib.request.urlretrieve(VOICE_JSON_URL, "voice.onnx.json")
        print("✅ Voice Model ready.")

setup_voice()

def speak(text):
    """Pipes text into the Piper executable and plays the resulting audio."""
    print("🗣️ Speaking...")
    
    # We run the hidden Piper executable and pipe the text directly into it
    process = subprocess.Popen(
        [r"piper\piper.exe", "-m", "voice.onnx", "--output_file", "speech.wav"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Pass the text to the executable
    process.communicate(input=text.encode('utf-8'))
    
    # Play the generated audio using Windows' built-in sound system
    if os.path.exists("speech.wav"):
        winsound.PlaySound("speech.wav", winsound.SND_FILENAME)

# Run this file directly to test the voice
if __name__ == "__main__":
    speak("Hello! I am Avian Echo, your personal edge AI bird guide.")