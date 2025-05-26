from flask import Blueprint, request, jsonify, render_template
from taskgen import generate_task, find_format_info
from prompt_builder import build_prompt
import random
from flask_login import current_user
from models import db
import json

interactive_blueprint = Blueprint("interactive", __name__)

# Допущенные типы с select на поле ответа
select_based_tasks = [
    "Multiple-choice Cloze",
    "Multiple Choice",
    "Multiple Matching",
    "Gapped Text"
]

@interactive_blueprint.route("/interactive_task", methods=["POST"])
def get_interactive_task():
    data = request.json
    exam = data["exam"]
    section = data["section"]
    task_type = data["task_type"]

    # Загружаем шаблонную инфу из task_templates.json через find_format_info
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

    # Случайный топик:
    default_topics = {
        "Reading": ["Technology", "Education", "Travel"],
        "Use of English": ["Culture", "Lifestyle", "Environment"],
    }
    topic = random.choice(default_topics.get(section, ["General"]))

    prompt1, _ = build_prompt(exam, section, task_type, topic, format_info)

    generated_task, _ = generate_task(
        exam=exam,
        task_type=task_type,
        topic=topic,
        section=section,
        model_choice="gpt-4o",
        prompt=prompt1
    )

    if current_user.is_authenticated:
        current_user.tasks_today += 1
        db.session.commit()

    return jsonify({"html": generated_task})

# ---------- Страницы ----------
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

    section_machine = section.lower()
    section_display = section_map.get(section_machine, section_machine)

    if section_machine == "use_of_english":
        task_types = ["Multiple-choice Cloze", "Open Cloze", "Word Formation", "Key Word Transformations"]
    elif section_machine == "reading":
        task_types = ["Multiple Matching", "Gapped Text", "Multiple Choice"]
    elif section_machine == "test":
        return render_template("test.html")
    else:
        task_types = []

    return render_template("select_task_types.html", section=section_display, levels=levels, task_types=task_types)

