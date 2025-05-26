from flask import Blueprint, request, jsonify, render_template
from taskgen import generate_task, find_format_info
from sentence_transformers import SentenceTransformer
import random
import json
from flask_login import current_user
from models import db
from typing import Dict, Tuple

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

    INPUT_HTML: Dict[str, str] = {
    # Use of English
    "Multiple-choice Cloze": (
        "<select name='{n}' class='answer-input blank' style='min-width:100px;text-align:center;'>"
        "<option value=''>—</option>"
        "<option value='A'>A</option>"
        "<option value='B'>B</option>"
        "<option value='C'>C</option>"
        "<option value='D'>D</option>"
        "</select>"
    ),
    # Reading
    "Multiple Choice": (
        "<select name='{n}' class='answer-input blank' style='min-width:100px;text-align:center;'>"
        "<option value=''>—</option>"
        "<option value='A'>A</option>"
        "<option value='B'>B</option>"
        "<option value='C'>C</option>"
        "<option value='D'>D</option>"
        "</select>"
    ),
    "Multiple Matching": (
        "<select name='{n}' class='answer-input blank' style='min-width:100px;text-align:center;'>"
        "<option value=''>—</option>"
        + "".join(f"<option value='{ltr}'>{ltr}</option>" for ltr in "ABCDEFGH")
        + "</select>"
    ),
    "Gapped Text": (
        "<select name='{n}' class='answer-input blank' style='min-width:100px;text-align:center;'>"
        "<option value=''>—</option>"
        + "".join(f"<option value='{ltr}'>{ltr}</option>" for ltr in "ABCDEFGH")
        + "</select>"
    ),
    "Word Formation": (
        "<div style='display:inline-flex;align-items:center;margin:0 4px;'>"
        "<input name='{n}' class='answer-input blank' "
        "style='width:140px;padding:4px;border:2px dashed #aaa;background:transparent;outline:none;text-align:center;'>"
        "<span style='margin-left:6px;font-weight:bold;'>(WORD)</span>"
        "</div>"
    ),
    "Key Word Transformations": (
        "<div style='display:inline-block;width:280px;margin:0 4px;vertical-align:bottom;border-bottom:2px dashed #aaa;'>"
        "<input name='{n}' class='answer-input blank' "
        "style='border:none;width:100%;background:transparent;outline:none;text-align:center;'>"
        "</div>"
    ),
    "Open Cloze": (
        "<div style='display:inline-block;width:160px;margin:0 4px;vertical-align:bottom;border-bottom:2px dashed #aaa;'>"
        "<input name='{n}' class='answer-input blank' "
        "style='border:none;width:100%;background:transparent;outline:none;text-align:center;'>"
        "</div>"
    ),
}
    input_html = INPUT_HTML[task_type]

        # --- Task‑specific heading -------------------------------------------------
    if task_type == "Key Word Transformations":
        task_block = (
            f"Generate one {task_type} item for the {exam} exam ({section}).\n"
            f"Provide two sentences.\n"
            f" • Sentence 1: the original idea.\n"
            f" • Sentence 2: starts similarly but contains ONE gap rendered with {input_html}. "
            f"The candidate must complete it with 2‑5 words using the given KEY WORD.\n"
            f"Print the KEY WORD in CAPITALS on a separate line just above sentence 2.\n"
            f"After sentence 2 add: '(Use 2–5 words. Do not change the word given.)'.\n"
        )
    elif task_type in ("Multiple-choice Cloze", "Multiple Choice"):
        task_block = (
            f"Generate a short text followed by numbered questions. "
            f"For each question, create exactly four answer choices labelled A), B), C), D).\n"
            f"Use the placeholder {input_html} **inside each gap** for Multiple-choice Cloze. "
            f"For classic Multiple Choice, list options below each question.\n"
        )
    elif task_type == "Multiple Matching":
        task_block = (
            "Generate a text (or several extracts) plus a list of statements. "
            "Each answer should be selected from letters A–H using the {input_html} field. "
            "Allow that one letter can be used more than once."
        )
    elif task_type == "Word Formation":
        task_block = (
            f"Generate a text ({exam} {task_type}) with gaps. "
            f"Place the base word for each gap in CAPITALS at the end of the line in brackets. "
            f"Inside the gap insert {input_html}."
        )
    else:
        task_block = ""

    # Обновлённый prompt с явными указаниями Gemma:
    prompt1 = (
        f"You are a Cambridge exams - FCE, CAE, CPE,  task generator."
        f"Generate a {task_type} task for the {exam} exam, section: {section}."
        f"Topic: {topic}."
        f"{task_block}"
        f"Instruction template: {instruction_example}\n"
        f"Format details: {format_desc}\n"
        f"Structure description: {structure_desc}\n"
        f"Layout notes: {layout_notes}\n"
        f"Visual guidelines: {visual_guidelines}\n"
        f"Min words: {min_words}; Max words: {max_words}.\n"
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


