import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# We use a 4-bit Quantized Gemma-2B model (Approx 1.6 GB)
MODEL_REPO = "bartowski/gemma-2-2b-it-GGUF"
MODEL_FILE = "gemma-2-2b-it-Q4_K_M.gguf"
MODEL_PATH = "gemma.gguf"

def download_brain():
    if not os.path.exists(MODEL_PATH):
        print(f"📥 Downloading Gemma-2B Brain (1.6 GB)... This takes a few minutes but only happens once.")
        # Download directly to the current folder
        downloaded_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, local_dir=".", local_dir_use_symlinks=False)
        os.rename(MODEL_FILE, MODEL_PATH)
        print("✅ Brain downloaded successfully!")

download_brain()

print("🧠 Loading Gemma into RAM...")
# Disable verbose logging so it doesn't flood your terminal during the hackathon demo
llm = Llama(model_path=MODEL_PATH, n_ctx=256, verbose=False)

def generate_lore(bird_name):
    """Feeds the bird name to Gemma and returns a 2-sentence description."""
    print(f"🤔 Thinking of lore for the {bird_name}...")
    
    # Strict prompt engineering for the hackathon
    prompt = f"User: You are an expert field guide. Describe the {bird_name} in exactly two short, fascinating sentences mentioning its behavior and appearance.\nAssistant:"
    
    response = llm(
        prompt,
        max_tokens=75,
        stop=["User:", "\n\n"],
        temperature=0.2 # Low temperature = highly deterministic, less rambling
    )
    
    return response['choices'][0]['text'].strip()

# Run this file directly to test the LLM
if __name__ == "__main__":
    lore = generate_lore("Northern Cardinal")
    print(f"\n🐦 Result: {lore}")