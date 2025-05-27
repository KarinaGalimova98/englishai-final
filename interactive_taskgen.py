from flask import Blueprint, request, jsonify, render_template
from taskgen import generate_task, find_format_info
from sentence_transformers import SentenceTransformer
import random
import pathlib, json
from flask_login import current_user
from models import db



interactive_blueprint = Blueprint("interactive", __name__)

select_based_tasks = [
    "Multiple-choice Cloze",       # Use of English
    "Multiple Choice",             # Reading
    "Multiple Matching",           # Reading
    "Gapped Text"                  # Reading
]

RULES = json.loads(pathlib.Path("task_format_rules.json").read_text(encoding="utf-8"))

def get_rules(task_type: str, exam: str) -> dict:
    block = RULES[task_type]
    return block.get(exam, block.get("all"))


# === HTML renderer (one function for all types) ==============================
def render_html(items: list, rules: dict) -> str:
    """Convert model JSON into ready‑to‑serve HTML using rules."""
    tpl = rules["input_html"]

    if rules["input_type"] == "select":
        labels = rules["option_labels"]

        def make_field(n, opts):
            opts_html = "".join(
                f"<option value='{lbl}'>{lbl}) {opt}</option>"
                for lbl, opt in zip(labels, opts)
            )
            return tpl.format(n=n, options=opts_html)
    else:  # input
        make_field = lambda n, _opts: tpl.format(n=n)

    html_blocks = []
    for i, it in enumerate(items, 1):
        field = make_field(i, it.get("options", []))
        html_blocks.append(
            f"<p>{it.get('text_before','')} {field} {it.get('text_after','')}</p>"
        )
    return "\n".join(html_blocks)

# === universal prompt builder ===============================================
def build_prompt(task_type: str, exam: str, rules: dict) -> str:
    p = ["You are a Cambridge Exams task generator."]

    if "num_gaps" in rules:
        n = rules["num_gaps"]
        p.append(f"Generate ONE {task_type} text for {exam} with EXACTLY {n} numbered gaps (1–{n}).")
    if "num_items" in rules:
        n = rules["num_items"]
        p.append(f"Generate EXACTLY {n} {task_type} items for {exam}.")
    if "num_questions" in rules:
        n = rules["num_questions"]
        p.append(f"Generate a text followed by {n} questions (A–D) for {exam}.")

    if "option_labels" in rules:
        p.append("For EACH gap/question provide options labeled " + ", ".join(rules["option_labels"]) + ".") 
    if "answer_length" in rules:
        p.append(f"Each answer must contain {rules['answer_length']}.") 

    p.append("Return ONLY JSON list with keys 'text_before', 'text_after', 'options' (if applicable). No HTML, no markdown.")
    return "\n".join(p)


def clean_json(s: str) -> str:
    """Удаляет все лишние символы до первой [ или {, а также обёртки ```json ... ```."""
    s = s.strip()
    # если начинается с ```
    if s.startswith("```"):
        # убираем все ```
        s = s.replace("```json", "").replace("```", "")
    # находим первую скобку
    first = min([s.find("{"), s.find("[")])
    if first > 0:
        s = s[first:]
    return s.strip()

@interactive_blueprint.route("/interactive_task", methods=["POST"])
def get_interactive_task():
    data = request.json
    exam = data["exam"]
    section = data["section"]
    task_type = data["task_type"]
    rules = get_rules(task_type, exam)


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

       
    # Обновлённый prompt с явными указаниями Gemma:
    prompt1 = (
        build_prompt(task_type, exam, rules)+ "\n"
        f"Topic: {topic}.\n"
        f"Instruction template: {instruction_example}\n"
        f"Format details: {format_desc}\n"
        f"Structure description: {structure_desc}\n"
        f"Layout notes: {layout_notes}\n"
        f"Visual guidelines: {visual_guidelines}\n"
        f"Min words: {min_words}; Max words: {max_words}.\n"
       
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

    clean = clean_json(generated_task)
    items = json.loads(clean)
    html  = render_html(items, rules)

    if current_user.is_authenticated:
        current_user.tasks_today += 1
        db.session.commit()

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


