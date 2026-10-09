import streamlit as st
import time
import numpy as np
import librosa
import os
import requests
from audio_capture import start_listening, audio_queue
from bird_classifier import identify_bird
from brain_llm import generate_lore
from voice_tts import speak

# Configure the web page
st.set_page_config(page_title="AvianEcho", page_icon="🐦", layout="centered")
st.title("🐦 AvianEcho")
st.subheader("Edge AI Bird Guide")

# Initialize memory state to save history
if "history" not in st.session_state:
    st.session_state.history = []

# Start the microphone stream in the background (only once)
@st.cache_resource
def get_audio_stream():
    return start_listening()

stream = get_audio_stream()

def get_real_bird_image_url(bird_name):
    """Fetches a real photograph of the exact bird species from Wikipedia."""
    formatted_name = bird_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_name}"
    
    try:
        # Wikipedia requires a User-Agent header for API requests
        response = requests.get(url, headers={"User-Agent": "AvianEchoApp/1.0"})
        if response.status_code == 200:
            data = response.json()
            # Try to get the high-res original image first, fallback to thumbnail
            if "originalimage" in data and "source" in data["originalimage"]:
                return data["originalimage"]["source"]
            elif "thumbnail" in data and "source" in data["thumbnail"]:
                return data["thumbnail"]["source"]
    except Exception:
        pass
        
    # Fallback placeholder if Wikipedia lacks an image for this specific bird
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png"

# Create UI Tabs for different modes
tab1, tab2 = st.tabs(["📁 Upload Audio", "🎙️ Live Microphone"])

with tab1:
    st.write("Upload a pre-recorded bird sound to analyze it.")
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3'])
    
    if uploaded_file is not None:
        st.audio(uploaded_file)
        
        if st.button("🔍 Identify Bird"):
            with st.spinner("Analyzing audio..."):
                with open("temp_upload.wav", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                audio_data, _ = librosa.load("temp_upload.wav", sr=48000, mono=True)
                
                if len(audio_data) > 144000:
                    start = (len(audio_data) - 144000) // 2
                    audio_data = audio_data[start:start+144000]
                elif len(audio_data) < 144000:
                    audio_data = np.pad(audio_data, (0, 144000 - len(audio_data)))
                    
                species, confidence = identify_bird(audio_data)
                
                if species:
                    st.success(f"**Detected: {species}** (Confidence: {confidence:.2f})")
                    
                    # 📸 Fetch and display the real Wikipedia image
                    image_url = get_real_bird_image_url(species)
                    st.image(image_url, caption=f"Photograph of {species} (via Wikipedia)", use_container_width=True)
                    
                    lore = generate_lore(species)
                    st.write(f"📖 *{lore}*")
                    speak(lore) 
                    
                    st.session_state.history.insert(0, {"bird": species, "conf": confidence, "lore": lore, "img": image_url})
                else:
                    st.error("No confident bird matches found in this audio file.")

with tab2:
    st.warning("⚠️ **Live Mode:** Turn this on to scan your microphone. (Disable to upload files smoothly!)")
    
    live_active = st.toggle("Activate Live Scanning")
    
    if live_active:
        st.info("🟢 Listening for bird calls in your environment...")
        
        if not audio_queue.empty():
            audio_data = audio_queue.get()
            species, confidence = identify_bird(audio_data)
            
            if species:
                st.success(f"**Live Detection: {species}** (Confidence: {confidence:.2f})")
                
                # 📸 Fetch and display the real Wikipedia image
                image_url = get_real_bird_image_url(species)
                st.image(image_url, caption=f"Photograph of {species} (via Wikipedia)", use_container_width=True)
                
                lore = generate_lore(species)
                st.write(f"📖 *{lore}*")
                speak(lore)
                
                st.session_state.history.insert(0, {"bird": species, "conf": confidence, "lore": lore, "img": image_url})
                
                with audio_queue.mutex:
                    audio_queue.queue.clear()
        
        time.sleep(0.5)
        st.rerun()

st.divider()
st.markdown("### 📜 Detection History")
for item in st.session_state.history:
    st.markdown(f"**{item['bird']}** ({item['conf']:.2f}) - *{item['lore']}*")