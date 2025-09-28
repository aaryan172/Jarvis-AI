import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
import subprocess
import platform

# === CONFIGURATION ===
FOLDER_PATH = r"Data"  # Folder where images will be stored
os.makedirs(FOLDER_PATH, exist_ok=True)  # ✅ Ensure folder exists

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}


# === CROSS-PLATFORM IMAGE OPENER ===
def open_with_default_app(file_path):
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        print(f"⚠️ Could not open {file_path}: {e}")


# === FUNCTION TO OPEN GENERATED IMAGES ===
def open_images(prompt: str):
    safe_prompt = prompt.replace(" ", "_")
    files = [f"{safe_prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(FOLDER_PATH, jpg_file)

        if os.path.exists(image_path):
            print(f"🖼️ Opening image: {os.path.abspath(image_path)}")
            open_with_default_app(image_path)
            sleep(1)  # Pause 1 sec before next
        else:
            print(f"❌ Image not found: {image_path}")


# === ASYNC FUNCTION TO CALL HUGGINGFACE API ===
async def query(payload: dict):
    response = await asyncio.to_thread(
        requests.post, API_URL, headers=headers, json=payload
    )
    return response.content


# === ASYNC FUNCTION TO GENERATE IMAGES ===
async def generate_images(prompt: str):
    tasks = []
    safe_prompt = prompt.replace(" ", "_")

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list, start=1):
        file_path = os.path.join(FOLDER_PATH, f"{safe_prompt}{i}.jpg")

        # ✅ Check if HuggingFace returned an error JSON
        if image_bytes.startswith(b"{"):
            print("⚠️ API returned error JSON instead of image:")
            print(image_bytes.decode("utf-8"))
            continue

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        print(f"✅ Saved {os.path.abspath(file_path)}")


# === WRAPPER FUNCTION ===
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Generate
    open_images(prompt)  # Open


# === MAIN LOOP TO LISTEN FOR REQUESTS ===
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read().strip()

        if not Data:
            sleep(1)
            continue

        Prompt, Status = Data.split(",")

        if Status.strip() == "True":
            print("🎨 Generating Images ...")
            GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")

            break
        else:
            sleep(1)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        sleep(1)
