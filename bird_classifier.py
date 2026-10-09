import os
import urllib.request
import numpy as np
import onnxruntime as ort

# Pointing to the stable edge-optimized ONNX model repository
MODEL_URL = "https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/BirdNET_v2.4_fp32.onnx"
LABELS_URL = "https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/labels.txt"

MODEL_PATH = "birdnet.onnx"
LABELS_PATH = "labels.txt"

def download_file(url, filename):
    """Downloads files and overwrites them if they are broken/empty."""
    # If the file exists but is empty (0 bytes) from a previous crash, remove it
    if os.path.exists(filename) and os.path.getsize(filename) < 1000:
        os.remove(filename)
        
    if not os.path.exists(filename):
        print(f"📥 Downloading {filename}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"✅ {filename} downloaded successfully!")

download_file(MODEL_URL, MODEL_PATH)
download_file(LABELS_URL, LABELS_PATH)

# Load the labels
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f.readlines()]

print("🧠 Loading ONNX Model into RAM...")
# Initialize the ONNX inference session
session = ort.InferenceSession(MODEL_PATH)
input_name = session.get_inputs()[0].name

def identify_bird(audio_array, min_confidence=0.70):
    """
    Takes a raw 3-second numpy array and runs it through the ONNX neural net.
    """
    if len(audio_array) != 144000:
        return None, 0.0
        
    # Shape the data for the tensor: [1 batch, 144000 samples]
    input_data = np.array([audio_array], dtype=np.float32)
    
    # Run the AI Inference using ONNX!
    outputs = session.run(None, {input_name: input_data})
    
    # This specific model outputs raw logits, so we apply a sigmoid 
    # to convert them into a 0 to 1 confidence percentage
    logits = outputs[0][0]
    probabilities = 1.0 / (1.0 + np.exp(-logits))
    
    max_index = np.argmax(probabilities)
    confidence = probabilities[max_index]
    
    if confidence > min_confidence:
        raw_label = labels[max_index]
        common_name = raw_label.split("_")[-1]
        return common_name, confidence
        
    return None, 0.0