import pygame  # for handling audio playback
import asyncio  # for asynchronous operations
import edge_tts  # for text-to-speech functionality
import os  # for file path handling
import re  # for regex to remove emojis
from dotenv import dotenv_values
from langdetect import detect, DetectorFactory

# Fix random results from langdetect
DetectorFactory.seed = 0

# Load environment variables from a .env file
env_vars = dotenv_values(".env")

# ✅ Map languages to proper Edge TTS voices
LANGUAGE_VOICE_MAP = {
    # English
    "en-US": "en-CA-LiamNeural",
    "en-IN": "en-IN-PrabhatNeural",
    "en-GB": "en-GB-RyanNeural",

    # Indian Languages
    "hi-IN": "hi-IN-SwaraNeural",      # Hindi
    "sa-IN": "sa-IN-AaravNeural",      # sanskrit
    "bho-IN": "bho-IN-SavitriNeural",    #bhojpori
    "bn-IN": "bn-IN-TanishaaNeural",    # Bengali
    "gu-IN": "gu-IN-DhwaniNeural",      # Gujarati
    "kn-IN": "kn-IN-SapnaNeural",       # Kannada
    "ml-IN": "ml-IN-SobhanaNeural",     # Malayalam
    "mr-IN": "mr-IN-AarohiNeural",      # Marathi
    "pa-IN": "pa-IN-SarikaNeural",      # Punjabi
    "ta-IN": "ta-IN-PallaviNeural",     # Tamil
    "te-IN": "te-IN-ShrutiNeural",      # Telugu
    "ur-IN": "ur-IN-GulNeural",         # Urdu
    
    # European
    "fr-FR": "fr-FR-DeniseNeural",
    "es-ES": "es-ES-ElviraNeural",
    "de-DE": "de-DE-KatjaNeural",
    "it-IT": "it-IT-ElsaNeural",
    "pt-PT": "pt-PT-FernandaNeural",
    "ru-RU": "ru-RU-SvetlanaNeural",

    # Asian
    "zh-CN": "zh-CN-XiaoxiaoNeural",
    "ja-JP": "ja-JP-NanamiNeural",
    "ko-KR": "ko-KR-SunHiNeural",

    # Arabic
    "ar-SA": "ar-SA-ZariyahNeural",
}

# ✅ Normalize langdetect → Edge TTS
LANGUAGE_CODE_NORMALIZER = {
    "en": "en-US",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "ur": "ur-IN",
    "fr": "fr-FR",
    "es": "es-ES",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-PT",
    "ru": "ru-RU",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ar": "ar-SA",
}

# Default fallback voice
DEFAULT_VOICE = env_vars.get("AssistantVoice", "en-CA-LiamNeural")

# ✅ Create global event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# ✅ Helper function to remove emojis
def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F900-\U0001F9FF"  # Supplemental symbols
        "\U0001FA70-\U0001FAFF"  # Extended symbols
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r"", text)


# ✅ Faster: Stream audio instead of saving first
async def TextToAudioFile(text: str, lang_code: str) -> str:
    file_path = r"Data/speech.mp3"

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

    voice = LANGUAGE_VOICE_MAP.get(lang_code, DEFAULT_VOICE)

    communicate = edge_tts.Communicate(text, voice, pitch='+5Hz', rate='+13%')

    # Stream and save quickly
    with open(file_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])

    return file_path


def TTS(text, func=lambda r=None: True):
    try:
        # ✅ Remove emojis before speaking
        clean_text = remove_emojis(text)

        # Detect language quickly
        try:
            detected = detect(clean_text)
        except:
            detected = "en"

        # Normalize language
        lang_code = LANGUAGE_CODE_NORMALIZER.get(detected, "en-US")

        # Generate & save audio faster (streaming)
        file_path = loop.run_until_complete(TextToAudioFile(clean_text, lang_code))

        # Play immediately
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")


def TextToSpeech(text, func=lambda r=None: True):
    words = text.split()
    
    if len(words) > 200:  # ✅ Speak only 200 words
        speak_part = " ".join(words[:200]) + ". The rest is on the screen."
        print(text)  # Full response still shown
        TTS(speak_part, func)
    else:
        TTS(text, func)


# -------------------------------
# Main execution block
# -------------------------------
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        if not user_input.strip():
            continue
        TextToSpeech(user_input)
