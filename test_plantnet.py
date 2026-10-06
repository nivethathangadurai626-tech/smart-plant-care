import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PLANTNET_API_KEY")

image_path = "plant_day_1.jpeg"

url = "https://my-api.plantnet.org/v2/identify/all"

with open(image_path, "rb") as image_file:

    files = {
        "images": image_file
    }

    data = {
        "organs": "leaf"
    }

    response = requests.post(
        url,
        params={"api-key": API_KEY},
        files=files,
        data=data
    )

print("STATUS CODE:", response.status_code)

print("RESULT:")

print(response.text[:3000])