import sys
from openai import OpenAI

# 1. Fix Windows console encoding for emojis
sys.stdout.reconfigure(encoding="utf-8") 

# 2. Setup the client to point to your LOCAL Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # Dummy key required by the library
)

# 3. Define the local model you have downloaded via Ollama
MODEL = "qwen3.5:4b" 

# 4. The Chat Function
def chat(user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful personal assistant."},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""

# 5. The Main Loop
if __name__ == "__main__":
    print(f"v0 assistant ({MODEL}) - ctrl+c to quit")
    try:
        while True:
            question = input("\nyou: ")
            print("\nassistant:", chat(question))
    except (EOFError, KeyboardInterrupt):
        print("\nbye!")