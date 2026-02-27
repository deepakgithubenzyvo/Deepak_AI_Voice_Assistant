import gradio as gr
import speech_recognition as sr
import subprocess
import webbrowser
import time
import os
import platform
import re
import json
from huggingface_hub import InferenceClient

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
ASSISTANT_NAME = "deepak"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

try:
    client = InferenceClient(model=HF_MODEL)
    USE_AI = True
except Exception:
    USE_AI = False

# ─────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are Deepak, a smart AI desktop assistant.
When the user asks you to perform a computer task, reply ONLY with valid JSON action blocks, one per line.
Format: {"action": "ACTION_NAME", "params": {"key": "value"}}

Actions available:
- open_app   -> params: {"app": "chrome"}
- open_url   -> params: {"url": "https://youtube.com"}
- search_web -> params: {"query": "levis tshirt size L"}
- screenshot -> params: {}
- close_app  -> params: {"app": "chrome"}

After the JSON lines, add a short human-readable message.
Example:
{"action": "open_url", "params": {"url": "https://www.youtube.com"}}
Opening YouTube for you!

For normal conversation, just reply normally without JSON."""

# ─────────────────────────────────────────────
#  APP & WEBSITE MAPS
# ─────────────────────────────────────────────
APP_COMMANDS = {
    "chrome":       {"windows": r"C:\Program Files\Google\Chrome\Application\chrome.exe", "darwin": "open -a 'Google Chrome'", "linux": "google-chrome"},
    "firefox":      {"windows": "firefox",   "darwin": "open -a Firefox",    "linux": "firefox"},
    "notepad":      {"windows": "notepad",   "darwin": "open -a TextEdit",   "linux": "gedit"},
    "calculator":   {"windows": "calc",      "darwin": "open -a Calculator", "linux": "gnome-calculator"},
    "file manager": {"windows": "explorer",  "darwin": "open .",             "linux": "nautilus"},
    "terminal":     {"windows": "cmd",       "darwin": "open -a Terminal",   "linux": "gnome-terminal"},
    "spotify":      {"windows": "spotify",   "darwin": "open -a Spotify",    "linux": "spotify"},
    "vscode":       {"windows": "code",      "darwin": "code",               "linux": "code"},
}

WEBSITE_MAP = {
    "youtube":   "https://www.youtube.com",
    "myntra":    "https://www.myntra.com",
    "amazon":    "https://www.amazon.in",
    "flipkart":  "https://www.flipkart.com",
    "google":    "https://www.google.com",
    "github":    "https://www.github.com",
    "netflix":   "https://www.netflix.com",
    "gmail":     "https://mail.google.com",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://www.twitter.com",
    "linkedin":  "https://www.linkedin.com",
    "whatsapp":  "https://web.whatsapp.com",
    "facebook":  "https://www.facebook.com",
    "reddit":    "https://www.reddit.com",
}

# ─────────────────────────────────────────────
#  RULE-BASED COMMAND PARSER (always runs first)
# ─────────────────────────────────────────────
def parse_command(text: str):
    """
    Detects intent directly from user text.
    Returns list of (action, params) tuples or None.
    """
    t = text.lower().strip()
    actions = []

    # --- screenshot ---
    if "screenshot" in t or "screen shot" in t:
        actions.append(("screenshot", {}))
        return actions, "Taking a screenshot!"

    # --- open app ---
    for app_name in APP_COMMANDS:
        if app_name in t:
            actions.append(("open_app", {"app": app_name}))
            return actions, f"Opening {app_name.title()} for you!"

    # --- open website ---
    for site, url in WEBSITE_MAP.items():
        if site in t:
            # Check if search/order intent alongside website
            search_keywords = ["search", "find", "order", "buy", "look for"]
            has_search = any(kw in t for kw in search_keywords)

            actions.append(("open_url", {"url": url}))

            if has_search and site in ["myntra", "amazon", "flipkart"]:
                # Extract what to search
                query = t
                for kw in search_keywords:
                    query = re.sub(rf'.*{kw}\s*', '', query)
                query = re.sub(rf'{site}', '', query).strip()
                if query:
                    actions.append(("search_web", {"query": f"{site} {query}"}))
                    return actions, f"Opening {site.title()} and searching for '{query}'!"

            return actions, f"Opening {site.title()} for you!"

    # --- google search ---
    search_match = re.search(r'search (?:for\s+)?(.+?)(?:\s+on google)?$', t)
    if search_match:
        query = search_match.group(1).strip()
        actions.append(("search_web", {"query": query}))
        return actions, f"Searching for '{query}' on Google!"

    return None, None

# ─────────────────────────────────────────────
#  ACTION EXECUTOR
# ─────────────────────────────────────────────
def get_os():
    s = platform.system().lower()
    if s == "darwin":  return "darwin"
    if s == "windows": return "windows"
    return "linux"

def run_action(action: str, params: dict) -> str:
    os_t = get_os()

    if action == "open_app":
        app = params.get("app", "").lower()
        cmd = None
        for key, cmds in APP_COMMANDS.items():
            if key in app:
                cmd = cmds.get(os_t, cmds.get("linux"))
                break
        if cmd:
            subprocess.Popen(cmd, shell=True)
            return f"✅ Opened: {app.title()}"
        else:
            subprocess.Popen(f"start {app}" if os_t == "windows" else f"open {app}", shell=True)
            return f"✅ Tried to open: {app}"

    elif action == "open_url":
        url = params.get("url", "")
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"✅ Opened: {url}"

    elif action == "search_web":
        query = params.get("query", "")
        webbrowser.open("https://www.google.com/search?q=" + query.replace(' ', '+'))
        return f"✅ Searched Google for: {query}"

    elif action == "screenshot":
        try:
            import pyautogui
            img  = pyautogui.screenshot()
            path = os.path.join(os.path.expanduser("~"), "deepak_screenshot.png")
            img.save(path)
            return f"✅ Screenshot saved to: {path}"
        except ImportError:
            return "⚠️ Run: pip install pyautogui"

    elif action == "type_text":
        try:
            import pyautogui
            time.sleep(0.5)
            pyautogui.typewrite(params.get("text", ""), interval=0.05)
            return "✅ Typed text"
        except ImportError:
            return "⚠️ Run: pip install pyautogui"

    elif action == "press_key":
        try:
            import pyautogui
            pyautogui.press(params.get("key", "enter"))
            return f"✅ Pressed: {params.get('key')}"
        except ImportError:
            return "⚠️ Run: pip install pyautogui"

    elif action == "close_app":
        app = params.get("app", "").lower()
        if os_t == "windows":
            subprocess.run(f"taskkill /f /im {app}.exe", shell=True)
        else:
            subprocess.run(f"pkill -f {app}", shell=True)
        return f"✅ Closed: {app}"

    return f"❓ Unknown action: {action}"

def execute_actions_from_list(actions_list):
    """Execute list of (action, params) tuples."""
    logs = []
    for action, params in actions_list:
        logs.append(run_action(action, params))
    return "\n".join(logs)

def execute_actions_from_text(text: str):
    """Parse JSON action blocks from AI response text and execute them."""
    logs = []
    # Match valid complete JSON objects
    json_pattern = re.compile(r'\{[^{}]*"action"\s*:\s*"[^"]+"\s*,[^{}]*"params"\s*:\s*\{[^{}]*\}[^{}]*\}')
    matches = json_pattern.findall(text)

    for block in matches:
        try:
            data   = json.loads(block)
            action = data.get("action", "")
            params = data.get("params", {})
            logs.append(run_action(action, params))
        except json.JSONDecodeError:
            pass  # skip malformed JSON silently

    return "\n".join(logs)

# ─────────────────────────────────────────────
#  AI RESPONSE
# ─────────────────────────────────────────────
def get_ai_response(user_message: str, history: list) -> str:
    if not USE_AI:
        return ""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        if isinstance(msg, dict) and "role" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})
    try:
        response = client.chat_completion(messages=messages, max_tokens=300, temperature=0.3)
        return response.choices[0].message.content
    except Exception:
        return ""

# ─────────────────────────────────────────────
#  SPEECH TO TEXT
# ─────────────────────────────────────────────
def transcribe_audio(audio_path) -> str:
    if audio_path is None:
        return ""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except Exception:
        return ""

# ─────────────────────────────────────────────
#  MAIN CHAT FUNCTION
# ─────────────────────────────────────────────
def chat(message: str, audio, history: list):
    # Transcribe voice if provided
    if audio is not None:
        transcribed = transcribe_audio(audio)
        if transcribed:
            message = transcribed

    if not message or not message.strip():
        return history, history, "", None

    # Strip wake-word prefix (e.g. "Deepak, " or "deepak ")
    clean_msg = re.sub(rf'^{ASSISTANT_NAME}[,!\s]*', '', message, flags=re.IGNORECASE).strip()
    if not clean_msg:
        clean_msg = message

    # Add user message to history
    history = history + [{"role": "user", "content": message}]

    action_log  = ""
    display     = ""

    # ── Step 1: Try rule-based parser first (fast & reliable) ──
    actions_list, rule_reply = parse_command(clean_msg)

    if actions_list:
        action_log = execute_actions_from_list(actions_list)
        display    = rule_reply or "Done!"

    else:
        # ── Step 2: Try AI model ──
        ai_response = get_ai_response(clean_msg, history)

        if ai_response:
            # Try to execute any JSON actions the AI returned
            ai_action_log = execute_actions_from_text(ai_response)
            # Strip JSON from display text
            display = re.sub(r'\{[^{}]*"action"[^{}]*\}', '', ai_response).strip()
            display = re.sub(r'\n{2,}', '\n', display).strip()
            if not display:
                display = "Done!"
            action_log = ai_action_log
        else:
            # ── Step 3: Final fallback — just respond helpfully ──
            display = (
                f"I understood: \"{clean_msg}\"\n\n"
                "I can help you open apps and websites! Try:\n"
                "• **Deepak, open YouTube**\n"
                "• **Deepak, open Chrome**\n"
                "• **Deepak, open Myntra and search Levis T-shirt**\n"
                "• **Deepak, take a screenshot**"
            )

    if action_log:
        display += f"\n\n{action_log}"

    # Add assistant reply
    history = history + [{"role": "assistant", "content": display}]

    return history, history, "", None

# ─────────────────────────────────────────────
#  GRADIO 6.0 UI
# ─────────────────────────────────────────────
CSS = """
.gradio-container { max-width: 900px; margin: auto; font-family: 'Segoe UI', sans-serif; }
#title    { text-align:center; color:#6366f1; font-size:2em; font-weight:bold; margin-bottom:4px; }
#subtitle { text-align:center; color:#888; font-size:.9em; margin-bottom:16px; }
"""

with gr.Blocks(title="Deepak AI Assistant") as demo:
    gr.HTML('<div id="title">🤖 Deepak AI Assistant</div>')
    gr.HTML('<div id="subtitle">Voice + Text AI that controls your laptop — HuggingFace Free Models</div>')

    chatbot = gr.Chatbot(
        label="Deepak",
        height=460,
        avatar_images=("👤", "🤖"),
    )

    with gr.Row():
        with gr.Column(scale=4):
            msg_input = gr.Textbox(
                placeholder='e.g. "Deepak, open YouTube" or use the mic 🎤',
                label="Your Command",
                lines=2,
            )
        with gr.Column(scale=1):
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Voice Input",
            )

    with gr.Row():
        send_btn  = gr.Button("▶ Send", variant="primary", scale=3)
        clear_btn = gr.Button("🗑 Clear", scale=1)

    gr.Markdown("### 💡 Example Commands")
    gr.Examples(
        examples=[
            ["Deepak, open YouTube"],
            ["Deepak, open Chrome"],
            ["Deepak, open Myntra and search Levis T-shirt size L"],
            ["Deepak, open Gmail"],
            ["Deepak, open Amazon and search for headphones"],
            ["Deepak, take a screenshot"],
            ["Deepak, open Netflix"],
            ["Deepak, search for Python tutorials"],
        ],
        inputs=msg_input,
    )

    state = gr.State([])

    send_btn.click(
        fn=chat,
        inputs=[msg_input, audio_input, state],
        outputs=[chatbot, state, msg_input, audio_input],
    )
    msg_input.submit(
        fn=chat,
        inputs=[msg_input, audio_input, state],
        outputs=[chatbot, state, msg_input, audio_input],
    )
    clear_btn.click(
        fn=lambda: ([], [], "", None),
        outputs=[chatbot, state, msg_input, audio_input],
    )

    gr.Markdown("""
---
**Supported Apps:** Chrome · Firefox · Notepad · Calculator · Spotify · VS Code · Terminal  
**Supported Sites:** YouTube · Myntra · Amazon · Flipkart · Gmail · Netflix · Instagram · LinkedIn · WhatsApp · GitHub  
**Voice:** Click 🎤, speak your command, then click ▶ Send
""")

if __name__ == "__main__":
    print("=" * 52)
    print("  🤖  Deepak AI Assistant")
    print("  🌐  Open: http://localhost:7860")
    print("  🎤  Voice + Text commands supported")
    print("=" * 52)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        css=CSS,
    )
