
import time
import requests
import base64
import os
import concurrent.futures

class FusionBrainAPI31:
    def __init__(self, api_key, secret_key):
        self.URL = "https://api-key.fusionbrain.ai/"
        self.headers = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}"
        }

    def generate_image(self, prompt):
        payload = {
            "type": "GENERATE",
            "numImages": 1,
            "width": 1024,
            "height": 1024,
            "generateParams": {
                "query": prompt
            }
        }

        response = requests.post(
            self.URL + "key/api/v2/text2image/run",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        uuid = response.json()["uuid"]
        return uuid

    def get_image_base64(self, uuid, attempts=20, delay=2):
        for _ in range(attempts):
            resp = requests.get(self.URL + f"key/api/v2/text2image/status/{uuid}", headers=self.headers)
            data = resp.json()
            if data['status'] == 'DONE':
                return data['images'][0]
            elif data['status'] == 'FAIL':
                raise Exception("Image generation failed")
            time.sleep(delay)
        raise Exception("Image generation timed out")


def extract_image_descriptions_from(text):
    lines = text.split('\n')
    descriptions = [
        line.strip('-•–— ').strip() 
        for line in lines 
        if line.strip().startswith(('-', '•', '–', '—'))
    ]
    return [desc for desc in descriptions if desc][:3]

def save_base64_image(base64_data, filename, folder="static/generated_images"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_data))
    return "/" + file_path.replace("\\", "/")

def generate_one_image(desc, api, index):
    try:
        if not desc.strip():
            print(f"⚠ Пустое описание — пропускаем изображение {index+1}")
            return None

        uuid = api.generate_image(desc)
        base64_img = api.get_image_base64(uuid)
        filename = f"image_{int(time.time())}_{index}.jpg"
        url = save_base64_image(base64_img, filename)
        return url
    except Exception as e:
        print(f"❌ Ошибка генерации изображения для '{desc}':", str(e))
        return None

def generate_images_from_descriptions(descriptions, api_key, api_secret):
    if not descriptions:
        return []

    api = FusionBrainAPI31(api_key, api_secret)

    image_urls = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(generate_one_image, desc, api, i)
            for i, desc in enumerate(descriptions[:5])
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                image_urls.append(result)

    return image_urls

