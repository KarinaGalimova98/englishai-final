from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

# Загрузи ранее сохранённые задания
with open("task_data.json", encoding="utf-8") as f:
    data = json.load(f)

# Модель для эмбеддингов
model = SentenceTransformer("all-mpnet-base-v2")

texts = [f"{task['exam']} {task['section']} {task['task_type']}" for task in data]

embeddings = model.encode(texts, show_progress_bar=True)

# Индекс
d = np.array(embeddings).shape[1]
index = faiss.IndexFlatL2(d)
index.add(np.array(embeddings).astype("float32"))

# Сохрани всё
faiss.write_index(index, "task_index.faiss")
with open("task_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
