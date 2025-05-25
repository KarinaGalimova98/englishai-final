from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from flask import Flask, render_template, request
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from long_turn_image_service import extract_image_descriptions_from, generate_images_from_descriptions
import requests
from flask import session
from my_level_predictor import predict_level_combined  # Импорт из твоей модели


# Модель эмбеддингов
embed_model = SentenceTransformer("all-mpnet-base-v2") #  или all-MiniLM-L6-v2

# Индекс и корпус
index = faiss.read_index("task_index.faiss")
with open("task_data.json", encoding="utf-8") as f:
    task_data = json.load(f)

client = OpenAI(api_key = "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")
# ключ OpenAI
app = Flask(__name__, template_folder='templates')



# Функция вызова Claude-Sonnet 3.7
def generate_with_claude_sonnet(prompt: str, api_key: str) -> str:
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "anthropic/claude-3-sonnet-20240229",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1400,
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Функция вызова Deep Seek
def generate_with_deepseek(prompt: str, api_key: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "deepseek/deepseek-prover-v2:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Функция вызова Gemma 3 
def generate_with_gemma(prompt: str, api_key: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "google/gemma-3-27b-it:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]




# Находим нужный формат задания
def find_format_info(exam, section, task_type, templates):
    try:
        return templates[exam][section][task_type]
    except KeyError:
        return {}


def generate_task(exam, task_type,topic,section, model_choice="gpt"):
    query = f"{exam} {section} {task_type}"
    q_embed = embed_model.encode([query])
    D, I = index.search(np.array(q_embed).astype("float32"), k=3)
    examples = []
    image_examples = []
    

    for i in I[0]:
        task = task_data[i]
        if task["task_type"] == task_type and task["exam"] == exam and task["section"] == section:
            examples.append(task["text"])
            if "image_description" in task:
                descs = task["image_description"]
                if isinstance(descs, str):
                    descs = [descs]
                image_examples.extend(descs)
                

    if examples:
        print(f"\n🔍 [RAG] Найдены {len(examples)} похожих заданий:")
        for i, ex in enumerate(examples, 1):
            print(f"\nПример {i}:\n{ex[:100]}...\n")
    else:
        print("❌ [RAG] Не найдено ни одного примера.")


    with open("task_templates.json", encoding="utf-8") as f:
        templates = json.load(f)
    format_info = find_format_info(exam, section, task_type, templates)
    instruction_example = format_info.get("instruction_example", "")
    format_desc = format_info.get("format", "")
    structure_desc = format_info.get("structure_description", "")
    layout_notes = format_info.get("layout_notes", "")
    visual_guidelines = format_info.get("visual_guidelines", "")
    min_words = format_info.get("min_words")
    max_words = format_info.get("max_words")


    prompt = (
        "Ты понимаешь запросы на русском, но создаёшь задания на английском языке.\n\n"
        f"Вот примеры:\n" + "\n\n---\n\n".join(examples) + "\n\n"
        f"Сгенерируй новое задание из Кэбриджского  экзамена экзамен: {exam}, раздел: {section}, тип: {task_type}, тема: {topic}.\n"
        f"Инструкция: {instruction_example}\n"
        f"Формат: {format_desc}\n"
        f"Описание структуры: {structure_desc}\n"
        f"Оформление: {layout_notes}\n"
        f"Визуальные требования: {visual_guidelines}\n"
        f"Минимум слов в тексте: {min_words}\n"
        f"Максимум слов в тексте: {max_words}\n\n"
        f"Соблюдай стиль, как в примерах."
        f"Текст должен соответствовать формату и стилю Cambridge."
        f"В ответе **НЕ** указывай 'TASK TYPE', 'FOCUS', 'FORMAT', 'Page' и другие метаописания.\n"
        f"Покажи только то, что увидит студент на реальном экзамене: инструкция + задание. Никогда не давай правильные овтеты"
        
    )
    if not format_info:
            print(f"⚠️ Шаблон не найден: {exam} | {section} | {task_type}")
    
    if task_type.lower() == "long turn" and image_examples:
        prompt += "\n\nВот примеры описаний изображений из похожих заданий:\n"
        for desc in image_examples[:3]:
            prompt += f"- {desc}\n"
        prompt += (
            "\n\nТеперь сгенерируй новое задание Long Turn, "
            "а после него — добавь описания изображений в таком же формате (начиная с тире). "
            "Они будут использоваться для генерации картинок."
        )
            
    # Вызов модели по выбору
    if model_choice == "gpt":
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1400,
            temperature=0.6
        )
        generated = response.choices[0].message.content

    elif model_choice == "claude-sonnet":
        generated = generate_with_claude_sonnet(prompt, api_key="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")

    elif model_choice == "deepseek":
        generated = generate_with_deepseek(prompt, api_key="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")

    elif model_choice == "gemma":
        generated = generate_with_gemma(prompt, api_key="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")


    image_links = []

    if task_type.lower() == "long turn":
        descriptions = extract_image_descriptions_from(generated)
        image_links = generate_images_from_descriptions(descriptions, api_key="4AC43656FC9124DA70EA04B41897D9C5", api_secret="4950EBAB224E8176411B5AEB0E41D4F8")


    # print("=== EXTRACTED IMAGE PROMPTS ===")
    # print(extr act_image_descriptions_from(generated))

    # print("=== RETURNING IMAGES ===")
    # print(image_links)



    return generated, image_links


@app.route("/", methods=["GET", "POST"])
def index_route():
    result = ""
    images = []
    model_choice = request.form.get("model", "gpt")

    if request.method == "POST":
        exam = request.form.get("level")
        section = request.form.get("section")
        task_type = request.form.get("task_type")  
        topic = request.form.get("topic")
        if exam and task_type and topic:
            result, images = generate_task(exam, task_type, topic,section, model_choice)
    return render_template("ui4.html", result=result, images=images)




if __name__ == "__main__":
    app.run(debug=True)