
"""Centralised prompt and HTML input builders for all interactive Cambridge tasks."""
from typing import Dict, Tuple

# HTML snippets for inputs per task type
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

def build_prompt(
    exam: str,
    section: str,
    task_type: str,
    topic: str,
    format_info: Dict
) -> Tuple[str, str]:
    """Return (prompt, input_html) ready for generate_task."""
    input_html = INPUT_HTML[task_type]
    
    # Extract template information
    instruction_example = format_info.get("instruction_example", "")
    format_desc = format_info.get("format", "")
    structure_desc = format_info.get("structure_description", "")
    layout_notes = format_info.get("layout_notes", "")
    visual_guidelines = format_info.get("visual_guidelines", "")
    min_words = format_info.get("min_words")
    max_words = format_info.get("max_words")

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

    prompt = (
        f"You are a Cambridge Exams task generator (supports FCE, CAE, CPE).\n"
        f"Generate a {task_type} task for the {exam} exam, section: {section}."
        f"Topic: {topic}.\n"
        f"{task_block}"
        f"Instruction template: {instruction_example}\n"
        f"Format details: {format_desc}\n"
        f"Structure description: {structure_desc}\n"
        f"Layout notes: {layout_notes}\n"
        f"Visual guidelines: {visual_guidelines}\n"
        f"Min words: {min_words}; Max words: {max_words}.\n"
        "IMPORTANT RULES:\n"
        " - Do NOT reveal correct answers in the task.\n"
        " - Return a SINGLE HTML block only – no markdown, no backticks.\n"
        " - Insert fields exactly where the gap should be using the given HTML.\n"
        " - At the very end append: <script type='application/json' id='answers'>[\"ans1\", ...]</script>\n"
    )

    return prompt, input_html
