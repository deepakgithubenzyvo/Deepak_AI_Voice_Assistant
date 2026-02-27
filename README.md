# 🤖 Deepak AI Assistant

A voice-controlled AI desktop assistant powered by **HuggingFace free models** with a beautiful **Gradio UI** — runs entirely in VS Code!

---

## ✨ Features

- 🎤 **Speech-to-Text** — Speak commands using your microphone
- 🧠 **Free AI** — Uses HuggingFace's free Mistral-7B model (no paid API key needed)
- 💻 **Full Laptop Control** — Opens apps, websites, searches the web, takes screenshots
- 🛒 **Smart Shopping** — Say "open Myntra and search Levis T-shirt size L"
- 🌐 **Browser Control** — Opens Chrome, Firefox, any browser
- ⚡ **Gradio UI** — Beautiful web UI that runs at http://localhost:7860

---

## 🚀 Quick Start

### Step 1: Open in VS Code
```
Open the `deepak-ai` folder in VS Code
```

### Step 2: Install dependencies
Open the VS Code terminal (`Ctrl+`` `) and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the app
```bash
python app.py
```

Or press **F5** in VS Code (with the provided launch config).

The app will open automatically at **http://localhost:7860**

---

## 🗣️ Example Commands

| Say this... | What happens |
|-------------|-------------|
| `Deepak, open Chrome` | Opens Google Chrome |
| `Deepak, open Myntra` | Opens Myntra in browser |
| `Deepak, search Levis T-shirt size L on Myntra` | Opens Myntra search results |
| `Deepak, open YouTube` | Opens YouTube |
| `Deepak, take a screenshot` | Takes and saves a screenshot |
| `Deepak, open Amazon and search headphones` | Opens Amazon search |
| `Deepak, open Gmail` | Opens Gmail |

---

## 🔧 Supported Apps & Websites

**Apps:** Chrome, Firefox, Notepad/TextEdit, Calculator, File Manager, Terminal, Spotify, VS Code

**Websites:** Myntra, Amazon, Flipkart, YouTube, Google, GitHub, Netflix, Gmail, Instagram, Twitter, LinkedIn, WhatsApp Web

---

## 📁 Project Structure

```
deepak-ai/
├── app.py              ← Main application
├── requirements.txt    ← Python dependencies
├── setup_and_run.bat   ← Windows one-click setup
├── setup_and_run.sh    ← Linux/Mac one-click setup
├── .vscode/
│   ├── launch.json     ← VS Code debug config (F5 to run)
│   └── settings.json   ← VS Code settings
└── README.md           ← This file
```

---

## ⚙️ Customization

### Change Assistant Name
In `app.py`, line 12:
```python
ASSISTANT_NAME = "deepak"  # Change to any name you want
```

### Change AI Model
In `app.py`, line 13:
```python
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"  # Any free HF model
```

Other free models you can use:
- `"HuggingFaceH4/zephyr-7b-beta"`
- `"meta-llama/Llama-3.2-3B-Instruct"`
- `"google/gemma-2-2b-it"`

---

## ❓ Troubleshooting

**Microphone not working?**
- Allow microphone permissions in your browser when prompted
- Make sure `SpeechRecognition` is installed: `pip install SpeechRecognition`

**HuggingFace model rate limited?**
- The app has a built-in fallback for basic commands
- Or add your free HF token: set env variable `HUGGING_FACE_HUB_TOKEN=your_token`

**Chrome not opening?**
- Make sure Chrome is installed in the default location
- Or use: `Deepak, open https://www.google.com` to open URLs directly

**pyautogui errors on Linux?**
```bash
sudo apt-get install python3-tk python3-dev
pip install pyautogui
```

---

## 🆓 Completely Free!

- No OpenAI API key needed
- No paid subscriptions
- Uses HuggingFace's free inference API
- Speech recognition uses Google's free STT service
