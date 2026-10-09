import sys
import ollama

sys.stdout.reconfigure(encoding="utf-8")

MODEL = "qwen2.5:3b"

def chat(history):
    for chunk in ollama.chat(model=MODEL, messages=history, stream=True):
        yield chunk["message"]["content"]

if __name__ == "__main__":
    print(f"v0 assistant ({MODEL}) - type /quit to exit\n")

    history = [{"role": "system", "content": "You are a helpful personal assistant."}]

    while True:
        try:
            question = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break

        if not question:
            continue
        if question.lower() in ("/quit", "/exit"):
            print("bye!")
            break

        history.append({"role": "user", "content": question})
        print("\nassistant: ", end="", flush=True)

        full = ""
        for piece in chat(history):
            print(piece, end="", flush=True)
            full += piece
        print("\n")

        history.append({"role": "assistant", "content": full})