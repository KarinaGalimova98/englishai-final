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

        # HTML для каждого типа заданий:
    if task_type == "Multiple-choice Cloze":
        input_html = (
            "<select name='{n}' class='answer-input blank' style='min-width:100px; text-align:center;'>"
            "<option value=''>—</option>"
            "<option value='A'>A</option>"
            "<option value='B'>B</option>"
            "<option value='C'>C</option>"
            "<option value='D'>D</option>"
            "</select>"
        )
    elif task_type in ["Multiple Matching", "Gapped Text"]:
        input_html = (
            "<select name='{n}' class='answer-input blank' style='min-width:100px; text-align:center;'>"
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
    elif task_type == "Word Formation":
        input_html = (
            "<div style='display:inline-flex; align-items:center; margin:0 4px;'>"
            "<input name='{n}' class='answer-input blank' style='width:140px; padding:4px; border:2px dashed #aaa; background:transparent; outline:none; text-align:center;'>"
            "<span style='margin-left:6px; font-weight:bold;'>({WORD})</span>"
            "</div>"
        )
    else:  # Open Cloze, Key Word Transformations
        input_html = (
            "<div style='display:inline-block; width:160px; margin:0 4px; vertical-align:bottom; border-bottom:2px dashed #aaa;'>"
            "<input name='{n}' class='answer-input blank' style='border:none;width:100%;background:transparent;outline:none;text-align:center;'>"
            "</div>"
        )

    # Обновлённый prompt с явными указаниями Gemma:
    prompt1 = (
        f"You are a Cambridge English exam (FCE, CAE, CPE) task generator. "
        f"Generate an authentic {task_type} task for the {exam} exam, section: {section}. "
        f"Topic: {topic}. "
        f"Example instruction: {instruction_example}. "
        f"Task format: {format_desc}. "
        f"Structure: {structure_desc}. "
        f"Layout instructions: {layout_notes}. "
        f"Visual guidelines: {visual_guidelines}. "
        f"Minimum words: {min_words}. Maximum words: {max_words}. "

        "Instructions for output format:\n"
        "- NEVER show correct answers explicitly in the generated task.\n"
        "- Return exactly one HTML block only.\n"
        "- Insert input fields exactly where blanks should be.\n"

        "Strict requirements per task type:\n\n"

        "1. Multiple-choice Cloze:\n"
        "- For each gap, provide exactly FOUR answer choices labeled explicitly with letters A, B, C, D.\n"
        "- Clearly shuffle the answer options randomly (DO NOT always put the correct answer first).\n"
        "- Correct answers must ONLY be letters ('a', 'b', 'c', or 'd') corresponding to shuffled positions.\n"
        f"HTML format:\n{input_html}\n\n"

        "2. Multiple Matching, Gapped Text:\n"
        "- Provide clearly labeled gaps and choices (A–H), shuffled randomly.\n"
        "- Correct answers ONLY as lowercase letters.\n"
        f"HTML format:\n{input_html}\n\n"

        "3. Word Formation:\n"
        "- Provide the word given for transformation clearly in parentheses (CAPITALIZED) next to each gap.\n"
        "- Correct answers in JSON must be lowercase words (without parentheses).\n"
        f"HTML format exactly:\n{input_html}\n\n"

        "4. Open Cloze, Key Word Transformations:\n"
        "- NO letters or words provided beside gaps.\n"
        "- Correct answers in JSON are exact lowercase words or short phrases.\n"
        f"HTML format:\n{input_html}\n\n"

        "- At the end of the task, ALWAYS include JSON with answers exactly like:\n"
        "<script type='application/json' id='answers'>[\"answer1\", \"answer2\", ...]</script>\n"

        "Important rules:\n"
        "- NEVER provide a separate list of answer choices at the bottom.\n"
        "- Output HTML ONLY (no markdown, no backticks, no plain text).\n"
        "- Follow authentic Cambridge exam layout exactly."
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
