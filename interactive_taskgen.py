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

    # Multiple-choice Cloze только 4 варианта A-D
    if task_type == "Multiple-choice Cloze":
        input_html = (
            "<select name='{n}' class='answer-input blank' style='min-width:60px; text-align:center;'>"
            "<option value=''>—</option>"
            "<option value='A'>A</option>"
            "<option value='B'>B</option>"
            "<option value='C'>C</option>"
            "<option value='D'>D</option>"
            "</select>"
        )
    # Multiple Matching и Gapped Text до 8 вариантов (A–H)
    elif task_type in ["Multiple Matching", "Gapped Text"]:
        input_html = (
            "<select name='{n}' class='answer-input blank' style='min-width:60px; text-align:center;'>"
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
    # Word Formation с исходным словом справа
    elif task_type == "Word Formation":
        input_html = (
            "<div style='display:inline-flex; align-items:center; margin:0 4px;'>"
            "<input name='{n}' class='answer-input blank' style='border:none; width:140px; background:transparent; outline:none; text-align:center; border-bottom:2px dashed #aaa;'>"
            "<span style='margin-left:6px; font-weight:bold;'>({WORD})</span>"
            "</div>"
        )
    # Остальные (Open Cloze, Key Word Transformations и т.д.)
    else:
        input_html = (
            "<div style='display:inline-block; width:160px; margin:0 4px; vertical-align:bottom; border-bottom:2px dashed #aaa;'>"
            "<input name='{n}' class='answer-input blank' style='border:none;width:100%;background:transparent;outline:none;text-align:center;'>"
            "</div>"
        )

    # Обновлённый, чёткий и однозначный prompt:
    prompt1 = (
        f"You are a Cambridge English exam (FCE, CAE, CPE) task generator. "
        f"Generate a realistic {task_type} task for the {exam} exam, section: {section}. "
        f"Topic: {topic}. "
        f"Instruction example: {instruction_example} "
        f"Task format: {format_desc} "
        f"Structure description: {structure_desc} "
        f"Layout instructions: {layout_notes} "
        f"Visual guidelines: {visual_guidelines} "
        f"Minimum words: {min_words}. Maximum words: {max_words}. "

        "Output format instructions:\n"
        "- Do NOT show correct answers in the task itself.\n"
        "- Return one HTML block only.\n"
        "- Place input fields directly into the paragraphs where blanks are located.\n"

        "- Use the following formats exactly according to task type:\n\n"

        "1. Multiple-choice Cloze:\n"
        f"{input_html}\n"
        "- Provide exactly 4 answer choices per gap (A, B, C, D).\n"
        "- Correct answers must ONLY be the LETTERS (a, b, c, or d) in the JSON.\n"
        "Example JSON: [\"a\", \"d\", \"b\", ...]\n\n"

        "2. Multiple Matching, Gapped Text:\n"
        f"{input_html}\n"
        "- Clearly label each gap numerically.\n"
        "- Correct answers must ONLY be the LETTERS (a–h) in the JSON.\n"
        "Example JSON: [\"f\", \"a\", \"h\", ...]\n\n"

        "3. Word Formation:\n"
        f"{input_html}\n"
        "- Place provided transformation words clearly in parentheses next to the gaps (e.g., DEFINE).\n"
        "- Correct answers should be provided in JSON without parentheses, lowercase.\n"
        "Example JSON: [\"definition\", \"global\", ...]\n\n"

        "4. Open Cloze, Key Word Transformations:\n"
        f"{input_html}\n"
        "- No extra letters or words provided next to gaps.\n"
        "- Correct answers in JSON must be lowercase words or phrases exactly as they should appear.\n"
        "Example JSON: [\"have\", \"taken up\", ...]\n\n"

        "- At the end, always include a JSON script with correct answers exactly in this format:\n"
        "<script type='application/json' id='answers'>[\"answer1\", \"answer2\", ...]</script>\n"

        "Important:\n"
        "- Never list answer options separately at the bottom.\n"
        "- Output must contain only HTML tags (no markdown, no backticks, no plain text).\n"
        "- Format must closely replicate authentic Cambridge exam layout."
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
