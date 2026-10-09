# ============================================================
# 1. IMPORTS & SETUP
# ------------------------------------------------------------
# - Bring in stdlib + OpenAI client for talking to local Ollama.
# - Fix Windows console encoding for emoji/unicode.
# - Point the client at Ollama's OpenAI-compatible endpoint.
# - Define the model and the sandboxed WORKSPACE folder.
# ============================================================
import sys
import json
from pathlib import Path
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "qwen2.5:3b"

WORKSPACE = Path(__file__).parent / "workspace"


# ============================================================
# 2. TOOLS (the "hands")
# ------------------------------------------------------------
# - Plain Python functions that do actual work.
# - The model NEVER sees this code — only the schemas below.
# - TOOLS maps tool name → function so chat() can run them.
# ============================================================
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


# ============================================================
# 3. TOOL SCHEMAS (what the model sees)
# ------------------------------------------------------------
# - JSON descriptions of each tool sent on every request.
# - The model uses these to decide WHEN and HOW to call a tool.
# ============================================================
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


# ============================================================
# 4. chat(user_message) — one turn, with tool support
# ------------------------------------------------------------
# - Builds a fresh messages list (no memory across calls).
# - First API call: model may answer directly OR ask for tools.
# - If it wants tools: run them, append results to messages,
#   then make a SECOND API call so the model can answer using
#   the tool output.
# - Returns the final text answer.
# ============================================================
def chat(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful personal assistant."},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )
    message = response.choices[0].message

    # No tool requested → the model already answered.
    if not message.tool_calls:
        return message.content or ""

    # Tool(s) requested → append the model's request, run each tool,
    # and append the result so the model can see it.
    messages.append(message)
    for call in message.tool_calls:
        args = json.loads(call.function.arguments or "{}")
        print(f"  [tool] {call.function.name}({args})")
        result = TOOLS[call.function.name](**args)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result),
        })

    # Second call: model now sees tool output and answers.
    final = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return final.choices[0].message.content or ""


# ============================================================
# 5. MAIN LOOP
# ------------------------------------------------------------
# - Create workspace if missing.
# - Read user input, call chat(), print answer.
# - /quit not supported here — Ctrl+C (KeyboardInterrupt) exits.
# - Each call to chat() starts fresh (no memory).
# ============================================================
if __name__ == "__main__":
    print(f"v1 assistant ({MODEL}) - ctrl+c to quit")
    try:
        while True:
            question = input("\nyou: ")
            print("\nassistant:", chat(question))
    except (EOFError, KeyboardInterrupt):
        print("\nbye!")