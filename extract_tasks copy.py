import fitz
import re
import json
import pandas as pd
from openai import OpenAI


# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text

# def detect_task_type(text):
#     text_lower = text.lower()
#     for keyword, task_type in {
#         "essay": "Essay",
#         "email": "Email",
#         "letter": "Letter",
#         "report": "Report",
#         "review": "Review",
#         "article": "Article",
#         "story": "Story",
#         "multiple choice": "Multiple Choice",
#         "gapped text": "Gapped Text",
#         "multiple matching": "Multiple Matching",
#         "open cloze": "Open Cloze",
#         "word formation": "Word Formation",
#         "key word transformation": "Key Word Transformation",
#         "interview": "Interview",
#         "long turn": "Long Turn",
#         "collaborative task": "Collaborative Task",
#         "discussion": "Discussion"
#     }.items():
#         if keyword in text_lower:
#             return task_type
#     return "Unknown"



# client = OpenAI(api_key = "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")
# # Укажите ваш ключ API OpenAI
# def detect_task_type_with_gpt(text):
#     prompt = (
#         "You are an assistant trained to classify exam tasks. Read the task below and identify its type.\n"
#         "Return ONLY the task type. Examples: Essay, Review, Report, Multiple Choice, Open Cloze, Word Formation, etc.\n\n"
#         f"Task:\n{text}\n\n"
#         "Task Type:"
#     )

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=10,
#             temperature=0.0
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print("❌ GPT error:", e)
#         return "Unknown"


# def detect_section(task_type):
#     if task_type in ["Essay", "Email", "Letter", "Report", "Review", "Article", "Story"]:
#         return "Writing"
#     elif task_type in ["Multiple Choice", "Gapped Text", "Multiple Matching", "Open Cloze", "Word Formation", "Key Word Transformation"]:
#         return "Reading"
#     elif task_type in ["Interview", "Long Turn", "Collaborative Task", "Discussion"]:
#         return "Speaking"
#     else:
#         return "Unknown"



# def split_tasks(text, exam_name):
#     # более гибкое разделение задач по ключевым словам
#     task_splits = re.split(r'(?i)(?:Part|Task|Question)\s\d+|\n{2,}', text)
#     cleaned = []
#     for task in task_splits:
#         task = task.strip()
#         if len(task) > 100:
#             task_type = detect_task_type(task)
#             if task_type == "Unknown":
#                 task_type = detect_task_type_with_gpt(task)
#             cleaned.append({
#                 "exam": exam_name,
#                 "section": detect_section(task_type),
#                 "task_type": task_type,
#                 "text": task
#             })
#     return cleaned


# Пример
#text = extract_text_from_pdf("data\\FCE Practice Tests.pdf")
#tasks = split_tasks(text, "FCE")
#with open("fce_tasks.json", "w", encoding="utf-8") as f:
    #json.dump(tasks, f, indent=2, ensure_ascii=False)

# text = extract_text_from_pdf("data\\cae_practice_tests_revised.pdf")
# tasks = split_tasks(text, "CAE")
# with open("cae_tasks.json", "w", encoding="utf-8") as f:
#     json.dump(tasks, f, indent=2, ensure_ascii=False)

# text = extract_text_from_pdf("data\\KET.pdf")
# tasks = split_tasks(text, "KET")
# with open("ket_tasks.json", "w", encoding="utf-8") as f:
#     json.dump(tasks, f, indent=2, ensure_ascii=False)

# text = extract_text_from_pdf("data\\PET.pdf")
# tasks = split_tasks(text, "PET")
# with open("pet_tasks.json", "w", encoding="utf-8") as f:
#     json.dump(tasks, f, indent=2, ensure_ascii=False)

# text = extract_text_from_pdf("data\\CPE.pdf")
# tasks = split_tasks(text, "CPE")
# with open("cpe_tasks.json", "w", encoding="utf-8") as f:
#     json.dump(tasks, f, indent=2, ensure_ascii=False)

all_data = []
for filename in ["fce_tasks.json", "cae_tasks.json", "cpe_tasks.json"]:
    with open(filename, encoding="utf-8") as f:
        all_data.extend(json.load(f))

with open("task_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)