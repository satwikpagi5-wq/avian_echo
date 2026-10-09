import time
from audio_capture import start_listening, audio_queue
from bird_classifier import identify_bird

def main():
    stream = start_listening()
    
    try:
        while True:
            if not audio_queue.empty():
                print("🔊 Loud sound detected! Analyzing in memory...")
                
                # Grab the raw audio float array directly from the mic queue
                audio_data = audio_queue.get()
                
                # Pass the array directly into the TFLite model!
                species, confidence = identify_bird(audio_data)
                
                if species:
                    print(f"✅ BIRD DETECTED: {species} (Confidence: {confidence:.2f})")
                else:
                    print("❌ No confident bird sounds found in that chunk.")
                    
            time.sleep(0.1) # Small sleep to prevent maxing out the CPU loop
            
    except KeyboardInterrupt:
        print("\nStopping...")
        stream.stop()
        stream.close()

if __name__ == "__main__":
    main()