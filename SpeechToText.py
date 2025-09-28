from dotenv import dotenv_values
import os
import mtranslate as mt
import speech_recognition as sr
from langdetect import detect, DetectorFactory

# Fix random results from langdetect
DetectorFactory.seed = 0

# ---------------- Font Fix ----------------
import matplotlib
matplotlib.rcParams['font.family'] = 'Noto Sans Devanagari'  # Or "Mangal" if installed

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Get the current working directory.
current_dir = os.getcwd()

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

# Function to set assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query: str) -> str:
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]
    
    if query_words:
        if any(new_query.startswith(word) for word in question_words):
            if query_words[-1][-1] in ['.', '?', '!']:
                new_query = new_query[:-1] + "?"
            else:
                new_query += "?"
        else:
            if query_words[-1][-1] in ['.', '?', '!']:
                new_query = new_query[:-1] + "."
            else:
                new_query += "."
    return new_query.capitalize()

# Universal translator using mtranslate
def UniversalTranslator(Text: str, target_lang="en") -> str:
    translated = mt.translate(Text, target_lang, "auto")
    return translated.capitalize()

# Speech recognition with automatic language detection
def recognize_speech() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        SetAssistantStatus("Listening...")
        print(" 🎤 Speak now...")
        audio = recognizer.listen(source)

    try:
        # Step 1: Recognize raw text in default language (let’s use English model)
        Text = recognizer.recognize_google(audio, language="en-US")

        # Step 2: Detect the real language
        detected_lang = detect(Text)
        print(f" 🌍 Detected language: {detected_lang}")

        # Step 3: If not English, translate to English
        if detected_lang != "en":
            SetAssistantStatus("Translating...")
            Text = UniversalTranslator(Text, "en")

        return QueryModifier(Text)  # Always clean output

    except sr.UnknownValueError:
        return ""  # no speech detected
    except sr.RequestError:
        return "Could not request results from speech service."

# ------------------------------
# Main execution block
# ------------------------------
if __name__ == "__main__":
    while True:
        Query = recognize_speech()

        if not Query.strip():
            continue  

        if "jarvis" not in Query.lower():
            print(" (Idle mode) Waiting for wake word 'Jarvis'...")
            continue  

        os.system("cls" if os.name == "nt" else "clear")
        print(" ✅ Recognized:", Query)
