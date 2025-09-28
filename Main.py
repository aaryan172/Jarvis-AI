from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import recognize_speech
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys
import webbrowser
from AppOpener import open as appopen, close as appclose  # ✅ for app control

# ------------------------------
# Temporary fix for missing import
# ------------------------------
def TempDirectoryPath(filename):
    return rf"Data\{filename}"

# ------------------------------
# Environment variables
# ------------------------------
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# ------------------------------
# Image Generation Config
# ------------------------------
BASE_DIR = os.getcwd()  # ✅ dynamic project root
IMAGE_SIGNAL_DIR = os.path.join("Frontend", "Files")
IMAGE_SIGNAL_FILE = os.path.join(IMAGE_SIGNAL_DIR, "imagegeneration.data")
IMAGE_SCRIPT_PATH = os.path.join(BASE_DIR, "Backend", "imagegeneration.py")  # ✅ fixed path

# ------------------------------
# Functions
# ------------------------------
def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:
        if len(File.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
        Data = File.read()
    if len(Data) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File:
            File.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

# ------------------------------
# Main execution
# ------------------------------
def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ... ")
    Query = recognize_speech()

    # If nothing was heard, don’t spam
    if not Query.strip():
        SetAssistantStatus("Available ... ")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ... ")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    )

    # Check for image generation
    for queries in Decision:
        if "generate " in queries.lower():
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # Execute automation tasks
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                try:
                    clean_query = queries.strip().lower()
                    print(f"Running automation for: {clean_query}")

                    # ✅ Smart open/close handling
                    if clean_query.startswith("open "):
                        target = clean_query.replace("open ", "").strip()

                        # Known websites dictionary
                        websites = {
                            "youtube": "https://www.youtube.com",
                            "google": "https://www.google.com",
                            "twitter": "https://twitter.com",
                            "instagram": "https://www.instagram.com",
                            "facebook": "https://www.facebook.com",
                            "github": "https://github.com"
                        }

                        if target in websites:
                            url = websites[target]
                            webbrowser.get().open(url)  # ✅ open in default browser
                            ShowTextToScreen(f"{Assistantname} : Opening {target}")
                            TextToSpeech(f"Opening {target}")
                        else:
                            try:
                                appopen(target, match_closest=True)
                                ShowTextToScreen(f"{Assistantname} : Opening {target}")
                                TextToSpeech(f"Opening {target}")
                            except Exception:
                                webbrowser.open(f"https://www.google.com/search?q={target}")
                                ShowTextToScreen(f"{Assistantname} : I couldn't find {target} app, searching online instead.")
                                TextToSpeech(f"I couldn't find {target} app, searching online instead.")
                        TaskExecution = True

                    elif clean_query.startswith("close "):
                        app_name = clean_query.replace("close ", "")
                        appclose(app_name, match_closest=True)
                        ShowTextToScreen(f"{Assistantname} : Closing {app_name}")
                        TextToSpeech(f"Closing {app_name}")  
                        TaskExecution = True

                    else:
                        run(Automation(clean_query))
                        TaskExecution = True

                except Exception as e:
                    print(f"Automation error: {e}")

    # Execute image generation properly
    if ImageExecution:
        try:
            os.makedirs(IMAGE_SIGNAL_DIR, exist_ok=True)
            with open(IMAGE_SIGNAL_FILE, "w", encoding="utf-8") as file:
                file.write(f"{ImageGenerationQuery},True")

            # Tell user it's working
            Answer = f"Okay {Username}, I am generating your image now. Please wait..."
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ... ")
            TextToSpeech(Answer)

            # Run synchronously
            p1 = subprocess.Popen(
                [sys.executable, IMAGE_SCRIPT_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            stdout, stderr = p1.communicate()

            if stderr:
                print("Image generation error:", stderr.decode())

            DoneMessage = "Your image has been generated successfully."
            ShowTextToScreen(f"{Assistantname} : {DoneMessage}")
            SetAssistantStatus("Answering ... ")
            TextToSpeech(DoneMessage)

        except Exception as e:
            print(f"Error starting image generation: {e}")

    # Handle general and realtime queries
    if G and R:
        SetAssistantStatus("Searching ... ")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ... ")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ... ")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))  # ✅ ChatBot now uses HuggingFace
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ... ")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching ... ")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ... ")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))  # ✅ HuggingFace
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ... ")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ... ")
                os._exit(1)

# ------------------------------
# Threads
# ------------------------------
def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ... " in AIStatus:
                sleep(0.2)  # prevent spamming
            else:
                SetAssistantStatus("Available ... ")

def SecondThread():
    GraphicalUserInterface()

# ------------------------------
# Run Threads
# ------------------------------
thread2 = threading.Thread(target=FirstThread, daemon=True)
thread2.start()
SecondThread()

# ------------------------------
# Initial execution
# ------------------------------
InitialExecution()

if __name__ == "__main__":
    pass
