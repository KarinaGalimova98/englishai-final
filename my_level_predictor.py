import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from scipy.sparse import hstack, csr_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re

# === Шаг 1. Загрузка данных ===
texts_df = pd.read_csv("cefr_leveled_texts.csv").rename(columns={"label": "level"}).dropna()
grammar_df = pd.read_csv("Grammar_Features.csv")


# === Шаг 2. SBERT embeddings ===
model_st = SentenceTransformer('paraphrase-MiniLM-L6-v2')
X_sbert = model_st.encode(texts_df['text'].tolist(), show_progress_bar=False)


# === Шаг 3. TF-IDF ===
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words='english')
X_tfidf = vectorizer.fit_transform(texts_df['text'])


# === Шаг 4. Grammar features ===
X_grammar = grammar_df[['passive_count', 'modal_count', 'conditional_type_2', 'avg_sentence_len']]
grammar_scaler = StandardScaler().fit(X_grammar)
X_grammar_scaled = StandardScaler().fit_transform(X_grammar)


# === Шаг 5. Объединение ===

X_combined = hstack([
    csr_matrix(X_sbert),         # преобразуем SBERT в sparse
    X_tfidf,                     # TF-IDF уже sparse
    csr_matrix(X_grammar_scaled) # грамматика — sparse
])
y = texts_df['level']


X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, stratify=y, random_state=42)

model_combined = LogisticRegression(max_iter=1000)
model_combined.fit(X_train, y_train)
y_pred = model_combined.predict(X_test)


def extract_grammar_features(text):
    
    text = str(text).lower()
    words = re.findall(r'\b[a-z]+\b', text)
    total_words = len(words)
    total_sentences = max(1, text.count('.'))

    return [
        len(re.findall(r'\b(be|is|are|was|were|been|being)\s+\w+ed\b', text)) / total_sentences,
        len(re.findall(r'\b(would|could|should|might|may|can|must|shall|will)\b', text)) / total_words if total_words else 0,
        len(re.findall(r'\bif\s+\w+\s+(had|was|were)\b.*?\bwould\b', text)),
        total_words / total_sentences
    ]

def predict_level_combined(messages):
    # Объединяем все тексты пользователя в одну строку
    if isinstance(messages, list):
        text = " ".join([m["text"] for m in messages if isinstance(m, dict) and m.get("sender") == "user"])
    else:
        text = str(messages)

    text = text.lower()

    # Векторизация
    emb = model_st.encode([text])
    tfidf_vec = vectorizer.transform([text])
    grammar_vec = grammar_scaler.transform([extract_grammar_features(text)])

    # Объединение всех признаков
    full_vector = hstack([
        csr_matrix(emb),
        tfidf_vec,
        csr_matrix(grammar_vec)
    ])

    return model_combined.predict(full_vector)[0]




