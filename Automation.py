# ==================================
# Automation.py
# ==================================

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
import subprocess
import requests
import asyncio
import os

# ==============================
# Load Environment Variables
# ==============================
env = dotenv_values(".env")
HuggingFaceAPIKey = env.get("HuggingFaceAPIKey")  # ✅ Changed to HuggingFace
Username = env.get("Username", "User")

# ==============================
# HuggingFace Setup
# ==============================
messages = []

SystemChatBot = [
    {
        "role": "system",
        "content": (
            f"You are {Username}'s helpful AI assistant. "
            "You write content like letters, notes, emails, applications, and poems when asked."
        ),
    }
]

# ==============================
# Content Writer (on-demand only)
# ==============================
def Content(topic: str):
    def OpenNotepad(file):
        subprocess.Popen(["Notepad", file])

    def ContentWriterAI(prompt: str) -> str:
        messages.append({"role": "user", "content": prompt})

        payload = {
            "inputs": SystemChatBot + messages,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 1,
            },
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",  # ✅ HuggingFace Model
            headers={
                "Authorization": f"Bearer {HuggingFaceAPIKey}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response.raise_for_status()
        result = response.json()

        # ✅ HuggingFace returns generated_text
        if isinstance(result, list) and "generated_text" in result[0]:
            Answer = result[0]["generated_text"]
        else:
            Answer = str(result)

        messages.append({"role": "assistant", "content": Answer})
        return Answer.strip()

    topic_clean = topic.strip()
    ContentByAI = ContentWriterAI(topic_clean)

    filepath = rf"Data\{topic_clean.lower().replace(' ', '_')}.txt"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ContentByAI)

    OpenNotepad(filepath)
    return True

# ==============================
# Other Automation Functions
# ==============================
def GoogleSearch(query: str):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webopen(url)

def YoutubeSearch(query: str):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webopen(url)

def OpenWebsite(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webopen(url)

def OpenApplication(app: str):
    appopen(app, match_closest=True, output=True)

def CloseApplication(app: str):
    close(app, match_closest=True, output=True)

# ==============================
# Async Command Executor
# ==============================
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        cmd = command.lower()

        if cmd.startswith("content "):
            fun = asyncio.to_thread(Content, cmd.removeprefix("content "))
            funcs.append(fun)

        elif cmd.startswith("google "):
            fun = asyncio.to_thread(GoogleSearch, cmd.removeprefix("google "))
            funcs.append(fun)

        elif cmd.startswith("youtube "):
            fun = asyncio.to_thread(YoutubeSearch, cmd.removeprefix("youtube "))
            funcs.append(fun)

        elif cmd.startswith("open website "):
            fun = asyncio.to_thread(OpenWebsite, cmd.removeprefix("open website "))
            funcs.append(fun)

        elif cmd.startswith("open app "):
            fun = asyncio.to_thread(OpenApplication, cmd.removeprefix("open app "))
            funcs.append(fun)

        elif cmd.startswith("close app "):
            fun = asyncio.to_thread(CloseApplication, cmd.removeprefix("close app "))
            funcs.append(fun)

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True

# ==============================
# Test Run
# ==============================
if __name__ == "__main__":# ==================================
# Automation.py
# ==================================

 from AppOpener import close, open as appopen
from webbrowser import open as webopen
from dotenv import dotenv_values
from rich import print
import subprocess
import requests
import asyncio
import os

# ==============================
# Load Environment Variables
# ==============================
env = dotenv_values(".env")
HuggingFaceAPIKey = env.get("HuggingFaceAPIKey")  # ✅ HuggingFace Key
Username = env.get("Username", "User")

# ==============================
# HuggingFace Setup
# ==============================
messages = []

SystemChatBot = [
    {
        "role": "system",
        "content": (
            f"You are {Username}'s helpful AI assistant. "
            "You write content like letters, notes, emails, applications, and poems when asked."
        ),
    }
]

# ==============================
# Content Writer (on-demand only)
# ==============================
def Content(topic: str):
    def OpenNotepad(file):
        subprocess.Popen(["notepad.exe", file])

    def ContentWriterAI(prompt: str) -> str:
        messages.append({"role": "user", "content": prompt})

        payload = {
            "inputs": SystemChatBot + messages,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 1,
            },
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={
                "Authorization": f"Bearer {HuggingFaceAPIKey}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response.raise_for_status()
        result = response.json()

        # ✅ HuggingFace returns generated_text
        if isinstance(result, list) and "generated_text" in result[0]:
            Answer = result[0]["generated_text"]
        else:
            Answer = str(result)

        messages.append({"role": "assistant", "content": Answer})
        return Answer.strip()

    topic_clean = topic.strip()
    ContentByAI = ContentWriterAI(topic_clean)

    filepath = rf"Data\{topic_clean.lower().replace(' ', '_')}.txt"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ContentByAI)

    OpenNotepad(filepath)
    return True

# ==============================
# Other Automation Functions
# ==============================
def GoogleSearch(query: str):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webopen(url)

def YoutubeSearch(query: str):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webopen(url)

def OpenWebsite(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webopen(url)

def OpenApplication(app: str):
    try:
        print(f"[cyan]Trying to open {app}...[/cyan]")
        appopen(app, match_closest=True, output=True)
    except Exception as e:
        print(f"[red]App '{app}' not found. Searching online...[/red]")
        # ✅ If app not installed → search online
        GoogleSearch(app)

def CloseApplication(app: str):
    try:
        close(app, match_closest=True, output=True)
    except Exception:
        print(f"[yellow]Could not close {app}. Maybe it is not running.[/yellow]")

# ==============================
# Async Command Executor
# ==============================
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        cmd = command.lower()

        if cmd.startswith("content "):
            fun = asyncio.to_thread(Content, cmd.removeprefix("content "))
            funcs.append(fun)

        elif cmd.startswith("google "):
            fun = asyncio.to_thread(GoogleSearch, cmd.removeprefix("google "))
            funcs.append(fun)

        elif cmd.startswith("youtube "):
            fun = asyncio.to_thread(YoutubeSearch, cmd.removeprefix("youtube "))
            funcs.append(fun)

        elif cmd.startswith("open website "):
            fun = asyncio.to_thread(OpenWebsite, cmd.removeprefix("open website "))
            funcs.append(fun)

        elif cmd.startswith("open app "):
            fun = asyncio.to_thread(OpenApplication, cmd.removeprefix("open app "))
            funcs.append(fun)

        elif cmd.startswith("close app "):
            fun = asyncio.to_thread(CloseApplication, cmd.removeprefix("close app "))
            funcs.append(fun)

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True
