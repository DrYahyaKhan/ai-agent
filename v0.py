import sys
import ollama

# 1. Fix Windows console encoding for emojis
sys.stdout.reconfigure(encoding="utf-8")

# 2. Define the local model you have downloaded via Ollama
MODEL = "qwen2.5:3b"

# 3. The Chat Function (streaming)
def chat(user_message: str) -> None:
    stream = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful personal assistant."},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )
    for chunk in stream:
        piece = chunk["message"]["content"]
        if piece:
            print(piece, end="", flush=True)
    print()  # final newline

# 4. The Main Loop
if __name__ == "__main__":
    print(f"v0 assistant ({MODEL}) - ctrl+c to quit")
    try:
        while True:
            question = input("\nyou: ")
            print("\nassistant:", end=" ", flush=True)
            chat(question)
    except (EOFError, KeyboardInterrupt):
        print("\nbye!")
