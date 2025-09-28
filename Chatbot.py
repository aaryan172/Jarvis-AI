from groq import Groq  # Importing the Groq library to use its API
from json import load, dump  # For saving and loading chat history
import datetime  # For real-time info
from dotenv import dotenv_values  # To load API keys from .env
import os

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")

# === Initialize Groq client ===
client = Groq(api_key=GroqAPIKey)

# === Ensure ChatLog file exists ===
if not os.path.exists("Data"):
    os.makedirs("Data")

if not os.path.exists(r"Data\ChatLog.json"):
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# === System instructions ===
System = f"""
Hello, I am {Username}, You are an advanced AI chatbot named {Assistantname}.
You show some emotion 😊, but stay professional. 
Do not tell time until asked, reply in English only, and avoid mentioning training data.
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# === Real-time info function ===
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds.\n"
    )

# === Cleanup function ===
def AnswerModifier(answer: str) -> str:
    lines = [line.strip() for line in answer.split("\n") if line.strip()]
    return "\n".join(lines)

# === Chatbot function ===
def ChatBot(Query: str):
    try:
        # Load old messages
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query
        messages.append({"role": "user", "content": Query})

        # Get response (non-streaming for stability)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ Updated model
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False  # ✅ Non-streaming for stable output
        )

        # ✅ FIXED: Access message content correctly
        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")

        # Append assistant response
        messages.append({"role": "assistant", "content": Answer})

        # Save updated log
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Reset chat log on error
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "⚠️ Something went wrong. Please try again."

# === Main Program ===
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
