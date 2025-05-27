from flask import Blueprint, request, jsonify, render_template
import numpy as np
from taskgen import generate_task, find_format_info
from sentence_transformers import SentenceTransformer
import random
import pathlib, json
from flask_login import current_user
from models import db
import faiss



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

    with open("task_format_rules.json", encoding="utf-8") as f:
        rules = json.load(f)
    task_block = rules[task_type]
    rule_info = task_block.get(exam, task_block.get("all", {}))
    section = rule_info.get("section", "")
    num_gaps = rule_info.get("num_gaps")
    input_type = rule_info.get("input_type", "")
    option_labels = rule_info.get("option_labels", [])
    input_html = rule_info.get("input_html", "")
    

    # Случайная тема по секции
    default_topics = {
        "Reading": ["Technology", "Education", "Travel"],
        "Use of English": ["Culture", "Lifestyle", "Environment"],
        "Grammar": ["Society", "Science", "Work"]
    }
    topic = random.choice(default_topics.get(section, ["General"]))

    examples = get_rag_examples(exam, section, task_type)
    # Обновлённый prompt с явными указаниями Gemma:
    prompt1 = (
        f"You are a Cambridge exams - FCE, CAE, CPE,  task generator."
        f"Generate a {task_type} task for the {exam} exam, section: {section}."
        f"Requirements: Strictly follow the Cambridge exam style. The task must include exactly the required number of gaps/items/questions, and the layout should be as in real Cambridge exam books.\n"
        f" Output format:\n"
        f"- Do NOT show correct answers in the task."
        f"- Return one HTML block only. Place input fields directly into the paragraph where the blank is."
        f"- Use this field format for each gap: {input_html} Do not list options at the bottom."
        f"- At the end, add this block:\n" 
        f"<script type='application/json' id='answers'>[\"correct1\", \"correct2\", \"correct3\",...]</script>\n"
        f"Do NOT use triple backticks or markdown formatting. Output only HTML."
        f"Input type: select (use '<select name=\"{{n}}\ class='answer-input blank'>{option_labels}</select>' for each gap/item)"
        f"EXAMPLES:\n" + "\n\n---\n\n".join(examples) + 
        f"Topic: {topic}.\n"
        f"Instruction template: {instruction_example}\n"
        f"Format details: {format_desc}\n"
        f"Structure description: {structure_desc}\n"
        f"Layout notes: {layout_notes}\n"
        f"Visual guidelines: {visual_guidelines}\n"
        f"Min words: {min_words}; Max words: {max_words}.\n"
        f"Number of gaps/items/questions: {num_gaps}\n"
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


