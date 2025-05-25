import json
import time
import requests
import base64
import os

class FusionBrainAPI:
    def __init__(self, api_key, secret_key):
        self.URL = "https://api-key.fusionbrain.ai/"
        self.headers = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}"
        }

    def get_pipeline(self):
        response = requests.get(self.URL + "key/api/v1/pipelines", headers=self.headers)
        response.raise_for_status()
        return response.json()[0]['id']

    def generate_image(self, prompt, pipeline_id):
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": 1024,
            "height": 1024,
            "generateParams": {
                "query": prompt
            }
        }

        files = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }

        print(f"📤 Отправка в Kandinsky: {prompt}")
        response = requests.post(
            self.URL + "key/api/v1/pipeline/run",
            headers=self.headers,
            files=files
        )
        print("📥 Ответ от Kandinsky:", response.status_code)
        response.raise_for_status()
        return response.json()['uuid']

    def get_image_base64(self, uuid, attempts=20, delay=2):
        for _ in range(attempts):
            resp = requests.get(self.URL + "key/api/v1/pipeline/status/" + uuid, headers=self.headers)
            data = resp.json()
            if data['status'] == 'DONE':
                return data['result']['files'][0]  # base64 строка
            time.sleep(delay)
        raise Exception("Image generation timed out")

def extract_image_descriptions_from(text):
    """
    Ищет в тексте Long Turn описания изображений (строки, начинающиеся на '-')
    """
    lines = text.split('\n')
    return [line.strip('-•–— ').strip() for line in lines if line.strip().startswith(('-', '•', '–', '—'))][:3]

def save_base64_image(base64_data, filename, folder="static/generated_images"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_data))
    return "/" + file_path.replace("\\", "/") 


def generate_images_from_descriptions(descriptions, api_key, api_secret):
    """
    Генерирует изображения по описаниям, сохраняет как файлы и возвращает URL-ы.
    """
    if not descriptions:
        return []

    api = FusionBrainAPI(api_key, api_secret)
    pipeline_id = api.get_pipeline()

    image_urls = []
    for i, desc in enumerate(descriptions[:5]):
        try:
            uuid = api.generate_image(desc, pipeline_id)
            base64_img = api.get_image_base64(uuid)
            filename = f"image_{int(time.time())}_{i}.jpg"
            url = save_base64_image(base64_img, filename)
            image_urls.append(url)
        except Exception as e:
            print(f"❌ Ошибка генерации изображения для '{desc}':", str(e))
    return image_urls

