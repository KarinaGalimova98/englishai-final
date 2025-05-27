from flask import Blueprint, request, jsonify, render_template
import numpy as np
from sentence_transformers import SentenceTransformer
import random
import  json
from flask_login import current_user
from models import db
import faiss
from dotenv import load_dotenv
import os
import base64
import requests
import json

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_KEY")

interactive_blueprint = Blueprint("interactive", __name__)

embed_model = SentenceTransformer("all-mpnet-base-v2")
index = faiss.read_index("task_index.faiss")
with open("task_data.json", encoding="utf-8") as f:
    task_data = json.load(f)

select_based_tasks = [
    "Multiple-choice Cloze",       # Use of English
    "Multiple Choice",             # Reading
    "Multiple Matching",           # Reading
    "Gapped Text"                  # Reading
]


def get_rag_examples(exam, section, task_type, k=3):
    query = f"{exam} {section} {task_type}"
    q_embed = embed_model.encode([query])
    D, I = index.search(np.array(q_embed).astype("float32"), k)
    examples = []
    for i in I[0]:
        task = task_data[i]
        if task["task_type"] == task_type and task["exam"] == exam and task["section"] == section:
            examples.append(task["text"])
    return examples

def normalize_name(name):
    return name.strip().lower().replace("-", " ").replace("_", " ").replace("  ", " ")

def find_image_file(exam, task_type):
    folder = os.path.join("static", "exams_exmpls", exam)
    target = normalize_name(task_type)
    for fname in os.listdir(folder):
        fname_base = os.path.splitext(fname)[0]
        if normalize_name(fname_base) == target:
            return os.path.join(folder, fname)
    return None  # если не найдено
# Маппинг task_type на номер фото или на имя файла
TASK_IMAGE_MAP = {
    "Open Cloze": "1.jpg",
    "Word Formation": "2.jpg",
    "Key Word Transformations": "3.jpg",
    "Multiple-choice Cloze": "4.jpg",
    "Multiple Matching": "5.jpg",
    "Gapped Text": "6.jpg",
    "Multiple Choice": "7.jpg",
}

def render_html(items, rule_info):
    html = ""
    input_type = rule_info.get("input_type", "input")
    for i, item in enumerate(items, 1):
        before = item.get("text_before", "")
        after = item.get("text_after", "")
        # Для select (варианты)
        if input_type == "select" and "options" in item:
            options_html = "".join(
                f"<option value='{o}'>{o}</option>" for o in item["options"]
            )
            gap = f"<select name='{i}' class='answer-input blank'>{options_html}</select>"
        else:  # обычный input
            gap = f"<input name='{i}' class='answer-input blank'>"
        html += f"{before}{gap}{after} "
    return f"<div class='generated-task'>{html.strip()}</div>"

@interactive_blueprint.route("/interactive_task", methods=["POST"])
def get_interactive_task():
    data = request.json
    exam = data["exam"]
    section = data["section"]
    task_type = data["task_type"]

    # 1. Найди RAG-примеры (top 3)
    examples = get_rag_examples(exam, section, task_type)
    examples_text = "\n\n".join(f"{i+1}. {ex}" for i, ex in enumerate(examples))

    # 2. Найди фото для prompt
    
    photo_path = find_image_file(exam, task_type)
    print("PHOTO PATH:", photo_path)
    print("PHOTO EXISTS:", os.path.isfile(photo_path))
    if not photo_path:
        return jsonify({"html": "<b>Image file not found!</b>"}), 500

    # Кодируем в base64 (OpenRouter требует base64 для image_url)
    with open(photo_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    # 3. Собери prompt
    prompt_text = (
        "Below is a photo of a real Cambridge exam task of the required type.\n"
        "Your job is to generate a **completely new** task in exactly the same format and visual style, as shown on the photo.\n"
        "The content/topic and complexity must be like in the examples below.\n\n"
        "EXAMPLES (real Cambridge tasks):\n"
        f"{examples_text}\n\n"
        "Return ONLY a JSON array, where each gap/item is an object like this:\n"
        "  {'text_before': ..., 'text_after': ...}\n"
        "(Or include 'options' if it's a multiple choice or cloze, and 'keyword' for Key Word Transformations.)\n"
        "DO NOT return explanations, comments or markdown. Only pure JSON!"
    )
    print("PROMPT TEXT:", prompt_text)
    # 4. Запрос к OpenRouter (Llama-4 Maverick)cd
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator"
    }
    data_api = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }},
                    {"type": "text", "text": prompt_text}
                ]
            }
        ],
        "max_tokens": 2024,
        "temperature": 0.2
    }

    response = requests.post(api_url, headers=headers, json=data_api)
    print("RESPONSE STATUS:", response.status_code)
    try:
        answer = response.json()
        # Обычно Llama отвечает так:
        model_out = answer["choices"][0]["message"]["content"]
    except Exception as e:
        model_out = f"ERROR: {str(e)}\nRAW: {response.text}"

    # 5. Обрезаем до первого [
    idx = model_out.find("[")
    clean_json = model_out[idx:] if idx != -1 else model_out
    try:
        items = json.loads(clean_json)
        if not isinstance(items, list):
            items = [items]
    except Exception as e:
        items = [{"text_before": "Sorry, there was an error generating the task.", "text_after": str(e), "options": []}]

    # 6. Рендер как обычно
    # (используй свою render_html(items, rule_info) если надо, или просто как есть)
    html = render_html(items, {"input_type": "select" if task_type in ["Multiple-choice Cloze", "Multiple Choice", "Gapped Text", "Multiple Matching"] else "input"})

    return jsonify({"html": html})


@interactive_blueprint.route("/use_of_english")
def use_of_english_page():
    return render_template("use_of_english.html")

@interactive_blueprint.route("/select_task_types/<section>")
def select_task_type(section):
    levels = ["FCE", "CAE", "CPE"]
    section_map = {
        "use_of_english": "Use of English",
        "reading": "Reading",
        "test": "Test"
    }

    section_machine = section.lower()  # 'use_of_english'
    section_display = section_map.get(section_machine, section_machine)

    section = section.lower()
    if section == "use_of_english":
        task_types = ["Multiple-choice Cloze", "Open Cloze", "Word Formation", "Key Word Transformations"]
    elif section == "reading":
        task_types = ["Multiple Matching", "Gapped Text", "Multiple Choice"]
    elif section == "test":
        return render_template("test.html")
    else:
        task_types = []

    return render_template("select_task_types.html", section=section_display, levels=levels, task_types=task_types)