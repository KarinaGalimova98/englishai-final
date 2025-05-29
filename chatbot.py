from flask import Blueprint, render_template, request, session, redirect
import requests
from my_level_predictor import predict_level_combined
import markdown
from flask_login import current_user
from models import db
import os
from dotenv import load_dotenv
load_dotenv()

chat_blueprint = Blueprint('chat', __name__, template_folder='templates')

API_KEY = os.getenv("OPENROUTER_API_KEY")  #  OpenRouter
MODEL_ID = "deepseek/deepseek-chat-v3-0324:free"

SYSTEM_PROMPT = (
        """
        You are an English tutor helping Russian-speaking learners assess their CEFR level (A1–C2). Run a 15-turn diagnostic session in 3 structured parts.

        PART 1: Conversation (Turns 1–9)
        Ask 9 questions of increasing difficulty. Start with basic topics: hobbies, food, daily life. 
        If the student responds clearly, use more complex questions (opinions, comparisons, past events).
        If they give one-word answers, make frequent grammar mistakes, or use Russian — simplify your next question.
        Encourage full-sentence replies, but don’t correct or explain.

        PART 2: Grammar Tasks (Turns 10–14)
        Give 5 grammar mini-tasks, one at a time. Keep them short and simple.
        Cover these types: 
        - articles or prepositions, 
        - verb tense (present/past),
        - word formation (e.g., cook → cooked),
        - phrasal verbs or modals,
        - sentence structure or word order.

        Just accept the answer and move to the next task.

        PART 3: Writing Task (Turn 15)
        Ask the student to write 3–6 sentences on one of the following:
        - A country you’d like to visit and why.
        - What you would change at your school or job.
        - Someone who inspires you.
        - What’s more important: freedom or safety?

        At the end, reply with their level:
        Your estimated English level is: A1 / A2 / B1 / B2 / C1 / C2

        Never use Russian. If the student uses it, just rephrase your last question in easier English.
        Start with: “What do you like to do in your free time?”
        """
)

def ask_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": request.host_url.rstrip('/'),  # или твой домен
        "X-Title": "English ChatBot",
        "Content-Type": "application/json"
    }

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        full_messages.append({
            "role": "user" if m["sender"] == "user" else "assistant",
            "content": m["text"]
        })

    payload = {
        "model": MODEL_ID,
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

@chat_blueprint.route("/chat", methods=["GET", "POST"])
def chat():
    messages = session.get("messages", [])
    result = None
    user_started = any(m["sender"] == "user" for m in messages)

    # 1. Первый вход — показываем приветствие
    if request.method == "GET" and not user_started:
        return render_template("chat.html", messages=messages, result=None, greeting=True)

    # 2. Если нажали “Начать”
    if request.method == "POST" and request.form.get("start") == "yes":
        try:
            bot_greeting = ask_openrouter([])
        except Exception as e:
            bot_greeting = f"(Ошибка: {str(e)})"
        messages = [{"sender": "bot", "text": markdown.markdown(bot_greeting)}]
        session["messages"] = messages
        return render_template("chat.html", messages=messages, result=None, greeting=False)

    # 3. Пользователь отправил сообщение через старую POST-форму
    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            messages.append({"sender": "user", "text": user_text})
            user_reply_count = len([m for m in messages if m["sender"] == "user"])
            if user_reply_count <= 15:
                try:
                    bot_reply = ask_openrouter(messages)
                except Exception as e:
                    bot_reply = f"(Ошибка: {str(e)})"
                messages.append({"sender": "bot", "text": markdown.markdown(bot_reply)})
            else:
                level_request = messages + [{
                    "sender": "user",
                    "text": "Please stop the lesson and estimate my English level. Only answer with a CEFR level from A1 to C2."
                }]
                try:
                    llm_level = ask_openrouter(level_request)
                except Exception as e:
                    llm_level = f"(Ошибка: {str(e)})"
                try:
                    combined_pred = predict_level_combined(messages)
                except Exception as e:
                    combined_pred = f"(Ошибка предсказания: {str(e)})"

                result = (
                    "<div class='bg-white text-indigo-900 rounded-xl shadow-md p-6 text-center text-lg font-semibold'>"
                    "🎉 <strong>Поздравляем! Вы прошли тест.</strong><br><br>"
                    f"🤖 <strong>Бот оценил ваш уровень как</strong>: <span class='text-purple-700'>{llm_level}</span><br>"
                    f"📊 <strong>Наша обученная модель оценила ваш уровень</strong> как: <span class='text-indigo-600'>{combined_pred}</span>"
                    "</div>"
                )
        session["messages"] = messages
        session.modified = True
        if current_user.is_authenticated:
            current_user.chatbot_today += 1
            db.session.commit()
        return render_template("chat.html", messages=messages, result=result, greeting=False)

    # 4. Если GET и чат уже был начат — показать чат!
    if request.method == "GET" and user_started:
        return render_template("chat.html", messages=messages, result=None, greeting=False)

    # 5. На всякий случай: если ничего не сработало — показать приветствие
    return render_template("chat.html", messages=messages, result=None, greeting=True)





@chat_blueprint.route("/chat/reset", methods=["POST"])
def reset_chat():
    session.pop("messages", None)  # очищаем историю
    session["messages"] = []
    return redirect("/chat")       # возвращаем пользователя обратно в чат
