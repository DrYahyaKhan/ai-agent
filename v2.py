# ============================================================
# v2.py — Local AI agent with tools + a bounded agent loop
# ------------------------------------------------------------
# Improvements over v1:
#   - Agent loop can chain multiple tool calls in one turn
#   - MAX_STEPS cap prevents infinite loops
#   - Tool errors don't crash the script
#   - Uses qwen2.5:7b for more reliable tool-calling
# ============================================================

# ---------- 1. Imports & setup ----------
# sys/json/Path/OpenAI: needed for encoding, JSON parsing,
# file paths, and talking to local Ollama.
# The client points at Ollama's OpenAI-compatible endpoint.
import sys
import json
from pathlib import Path
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "qwen2.5:7b"

WORKSPACE = Path(__file__).parent / "workspace"


# ---------- 2. Tools (real Python functions) ----------
# The model NEVER sees this code — it only sees the schemas below.
# TOOLS is a dispatch table: name → function.
def list_files() -> str:
    """List the files in the assistant's workspace folder."""
    return "\n".join(p.name for p in WORKSPACE.iterdir()) or "(empty)"

def read_file(filename: str) -> str:
    """Read a file from the workspace folder."""
    path = WORKSPACE / filename
    if not path.is_file():
        return f"error: no file named {filename}"
    return path.read_text(encoding="utf-8")

TOOLS = {"list_files": list_files, "read_file": read_file}


# ---------- 3. Tool schemas (what the model sees) ----------
# JSON descriptions sent on every request. The model uses these
# to decide WHEN and HOW to call each tool.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the workspace folder.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the workspace folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read",
                    }
                },
                "required": ["filename"],
            },
        },
    },
]


# ---------- 4. The agent loop ----------
# This is the whole trick:
#   1. Send messages + tools to the model.
#   2. If the model replies with text → return it (done).
#   3. If the model asks for tools → run each one, append the
#      result to messages, and LOOP BACK so the model can
#      answer using the tool output.
#   4. Cap steps at MAX_STEPS so a confused model can't spin forever.
def run_agent(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful personal assistant."},
        {"role": "user", "content": user_message},
    ]

    MAX_STEPS = 5
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS
        )
        message = response.choices[0].message
        messages.append(message)

        # No tool requested → the model already answered.
        if not message.tool_calls:
            return message.content or ""

        # Tool(s) requested → run each and feed the result back.
        for call in message.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"  [tool] {call.function.name}({args})")
            try:
                result = TOOLS[call.function.name](**args)
            except Exception as e:
                result = f"Tool error: {e}"
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    return "Sorry — I couldn't finish that within the step limit."


# ---------- 5. Main loop ----------
# Create workspace, print banner, read input, call run_agent,
# print the answer. Ctrl+C / Ctrl+Z exits cleanly.
# Note: each call starts fresh (no memory across turns).
if __name__ == "__main__":
    WORKSPACE.mkdir(exist_ok=True)

    print(f"v2 agent ({MODEL}) - ctrl+c to quit")
    print(f"workspace: {WORKSPACE}\n")

    try:
        while True:
            question = input("you: ")
            if not question.strip():
                continue
            print("\nassistant: ", end="", flush=True)
            print(run_agent(question) + "\n")
    except (EOFError, KeyboardInterrupt):
        print("\nbye!")