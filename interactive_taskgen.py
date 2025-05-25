from flask import Blueprint, request, jsonify, render_template
from taskgen import generate_task, find_format_info
from sentence_transformers import SentenceTransformer
import random
import json
from flask_login import current_user
from models import db


interactive_blueprint = Blueprint("interactive", __name__)

select_based_tasks = [
    "Multiple-choice Cloze",       # Use of English
    "Multiple Choice",             # Reading
    "Multiple Matching",           # Reading
    "Gapped Text"                  # Reading
]

@interactive_blueprint.route("/interactive_task", methods=["POST"])
def get_interactive_task():
    data = request.json
    exam = data["exam"]
    section = data["section"]
    task_type = data["task_type"]

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

    # Случайная тема по секции
    default_topics = {
        "Reading": ["Technology", "Education", "Travel"],
        "Use of English": ["Culture", "Lifestyle", "Environment"],
        "Grammar": ["Society", "Science", "Work"]
    }
    topic = random.choice(default_topics.get(section, ["General"]))

    # Определяем, нужно ли использовать выпадающий список
    if task_type in select_based_tasks:
        input_html = (
            "<select name='{n}' class='answer-input blank'>"
            "<option value=''>—</option>"
            "<option value='A'>A</option>"
            "<option value='B'>B</option>"
            "<option value='C'>C</option>"
            "<option value='D'>D</option>"
            "<option value='E'>E</option>"
            "<option value='F'>F</option>"
            "<option value='G'>G</option>"
            "<option value='H'>H</option>"
            "</select>"
        )
    else:
        input_html = "<input name='{n}' class='answer-input blank'>"


    prompt1 = (
        f"You are a Cambridge exams - FCE, CAE, CPE,  task generator."
        f"Generate a {task_type} task for the {exam} exam, section: {section}."
        f"Topic: {topic}."
        f"Инструкция: {instruction_example}"
        f"Формат: {format_desc}"
        f"Описание структуры: {structure_desc}"
        f"Оформление: {layout_notes}"
        f"Визуальные требования: {visual_guidelines}"
        f"Минимум слов в тексте: {min_words}"
        f"Максимум слов в тексте: {max_words}"
        f" Output format:\n"
        f"- Do NOT show correct answers in the task."
        f"- Return one HTML block only. Place input fields directly into the paragraph where the blank is."
        f"- Use this field format for each gap: {input_html} Do not list options at the bottom."
        f"- At the end, add this block:\n" 
        f"<script type='application/json' id='answers'>[\"correct1\", \"correct2\", \"correct3\",...]</script>\n"
        f"Do NOT use triple backticks or markdown formatting. Output only HTML."
    )

    

    # Генерация задания с использованием GEMMA
    generated_task, _ = generate_task(
        exam=exam,
        task_type=task_type,
        topic=topic,
        section=section,
        model_choice="gemma",
        prompt = prompt1
    )

    if current_user.is_authenticated:
        current_user.tasks_today += 1
        db.session.commit()

    return jsonify({"html": generated_task})




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
