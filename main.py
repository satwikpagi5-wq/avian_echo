import time
from audio_capture import start_listening, audio_queue
from bird_classifier import identify_bird
from brain_llm import generate_lore
from voice_tts import speak

def main():
    print("🚀 Booting AvianEcho System...")
    
    # Start the continuous background listening stream
    stream = start_listening()
    print("🟢 Agent is active. Waiting for bird calls...")
    
    try:
        while True:
            if not audio_queue.empty():
                # 1. Grab the raw audio float array directly from the mic queue
                audio_data = audio_queue.get()
                
                # 2. Pass the array directly into the TFLite model
                species, confidence = identify_bird(audio_data)
                
                if species:
                    print(f"\n✅ BIRD DETECTED: {species} (Confidence: {confidence:.2f})")
                    
                    # 3. Get the description from Gemma
                    lore = generate_lore(species)
                    print(f"📖 Lore: {lore}")
                    
                    # 4. Read it out loud using Piper
                    speak(lore)
                    
                    # 5. Anti-Feedback Loop: Clear the queue so the AI doesn't 
                    # accidentally try to identify its own text-to-speech voice
                    with audio_queue.mutex:
                        audio_queue.queue.clear()
                        
                else:
                    # Optional: Print a dot just to show it's analyzing noise
                    print(".", end="", flush=True)
                    
            # Prevent the while loop from maxing out your CPU
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AvianEcho...")
        stream.stop()
        stream.close()

if __name__ == "__main__":
    main()