from flask import Blueprint, render_template, request, redirect, url_for, send_file, session
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import numpy as np
import faiss
import json
from sklearn.metrics.pairwise import cosine_similarity
from long_turn_image_service import extract_image_descriptions_from, generate_images_from_descriptions
from my_level_predictor import predict_level_combined
import requests
from flask import session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.units import cm
from reportlab.platypus import Spacer
from io import BytesIO
from flask_login import current_user
from models import db
from markupsafe import Markup
import markdown
import os
from dotenv import load_dotenv
load_dotenv()








task_blueprint = Blueprint("taskgen", __name__)
# Модель эмбеддингов
embed_model = SentenceTransformer("all-mpnet-base-v2") #  или all-MiniLM-L6-v2

# Индекс и корпус
index = faiss.read_index("task_index.faiss")
with open("task_data.json", encoding="utf-8") as f:
    task_data = json.load(f)

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
# ключ OpenAI


# Функция вызова Claude-Sonnet 3.7
def generate_with_claude_sonnet(prompt: str, api_key: str) -> str:
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "anthropic/claude-3-sonnet-20240229",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1400,
        "temperature": 0.5
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
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "deepseek/deepseek-prover-v2:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.5
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
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "qwen/qwq-32b:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Функция вызова GPT-4o Mini
def generate_with_gpt4o(prompt: str, api_key: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator"
    }

    data = {
        "model": "openai/gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_gemini(prompt: str, api_key: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.host_url.rstrip('/'),
        "X-Title": "Cambridge Task Generator",
        
    }
    data = {
        #"model": "google/gemini-2.5-flash-preview-05-20", 
        "model":"google/gemini-2.5-flash-preview-05-20",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3048,
        "temperature": 0.4,
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


def generate_task(exam, task_type,topic,section, model_choice="deepseek",prompt = None):
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

    if prompt is None:
        prompt = (
            "You understand instructions in Russian, but ALWAYS respond in **English only**."
            f"Here are some examples:\n" + "\n\n---\n\n".join(examples) + "\n\n"
            f"Generate a new Cambridge English exam task.\n"
            f"Exam: {exam}, Section: {section}, Task type: {task_type}, Topic: {topic}.\n"
            f"Instructions: {instruction_example}\n"
            f"Format: {format_desc}\n"
            f"Structure description: {structure_desc}\n"
            f"Layout notes: {layout_notes}\n"
            f"Visual requirements: {visual_guidelines}\n"
            f"Minimum word count: {min_words}\n"
            f"Maximum word count: {max_words}\n\n"
            f"Follow the style shown in the examples.\n"
            f"The text must match the format and tone of official Cambridge tasks.\n"
            f"⚠️ Do NOT include labels such as 'TASK TYPE', 'FOCUS', 'FORMAT', 'Page', or any other metadata.\n"
            f"Only show what a student would see on the real exam page: the instruction and the task itself.\n"
            f"NEVER provide correct answers.\n"
            f"IMPORTANT: Your response must be written in English only."
            
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

    elif model_choice == "claude":
        generated = generate_with_claude_sonnet(prompt, api_key=os.getenv("OPENROUTER_API_KEY"))

    elif model_choice == "deepseek":
        generated = generate_with_deepseek(prompt, api_key=os.getenv("OPENROUTER_API_KEY"))

    elif model_choice == "gemma":
        generated = generate_with_gemma(prompt, api_key=os.getenv("OPENROUTER_API_KEY"))

    elif model_choice == "gpt-4o":
        generated = generate_with_gpt4o(prompt, api_key=os.getenv("OPENROUTER_API_KEY"))

    elif model_choice == "gemini":
        generated = call_gemini(prompt, api_key=os.getenv("OPENROUTER_API_KEY"))


    


    image_links = []

    if task_type.lower() == "long turn":
        descriptions = extract_image_descriptions_from(generated)
        image_links = generate_images_from_descriptions(descriptions, api_key=os.getenv("KANDINSKY_KEY"), api_secret=os.getenv("KANDINSKY_SECRET_KEY"))


    # print("=== EXTRACTED IMAGE PROMPTS ===")
    # print(extr act_image_descriptions_from(generated))

    # print("=== RETURNING IMAGES ===")
    # print(image_links)



    return generated, image_links

@task_blueprint.app_template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text))



@task_blueprint.route("/", methods=["GET", "POST"])
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
            result, images = generate_task(exam, task_type, topic, section, model_choice)
            session['result'] = result
            session['images'] = images
        return redirect(url_for('taskgen.index_route'))    
    result = session.get('result', '')
    images = session.get('images', [])
    if current_user.is_authenticated:
        current_user.gpt_today += 1
        db.session.commit()

    return render_template("ui5.html", result=result, images=images)

@task_blueprint.route("/download_pdf")
def download_pdf():
    result = session.get("result", "")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story = []

    for line in result.strip().split("\n"):
        story.append(Paragraph(line.strip(), styles["Normal"]))
        story.append(Spacer(1, 11))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="task.pdf", mimetype="application/pdf")


