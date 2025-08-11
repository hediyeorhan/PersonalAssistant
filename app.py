from flask import Flask, render_template, request, jsonify
from agents.todo_agent import TodoAgent
from agents.note_agent import NoteAgent
from agents.reminder_agent import ReminderAgent
from agents.db_info_agent import DbInfoAgent
from services.router import classify_agent
from datetime import datetime

app = Flask(__name__)

# Agent örnekleri (tek sefer yarat)
todo_agent = TodoAgent()
note_agent = NoteAgent()
reminder_agent = ReminderAgent()
db_info_agent = DbInfoAgent()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").strip()
    extra_data = data.get("extra_data", None)

    if not user_input:
        return jsonify({"response": "Lütfen bir komut girin."})

    selected_agent = classify_agent(user_input)

    if selected_agent == "todo":
        result = todo_agent.handle_prompt(user_input, extra_data)
    elif selected_agent == "note":
        result = note_agent.handle_prompt(user_input, extra_data)
    elif selected_agent == "reminder":
        result = reminder_agent.handle_prompt(user_input, extra_data)
    elif selected_agent == "db_info":
        result = db_info_agent.handle_prompt(user_input)
    else:
        result = "Komut tanınamadı veya geçerli bir görev türü bulunamadı."

    return jsonify({"response": result})


# --- Bugün için yaklaşan hatırlatıcılar API'si ---
@app.route("/api/today_reminders")
def today_reminders():
    try:
        reminders = reminder_agent.get_today_reminders()
    except Exception as e:
        import traceback
        traceback.print_exc()  # Konsola ayrıntılı hata yazısı
        return jsonify({"error": f"Hatırlatıcılar alınamadı: {str(e)}"}), 500

    result = [
        {
            "id": r.id,
            "title": r.message,
            "due_date": r.remind_at.strftime("%H:%M")
        }
        for r in reminders
    ]
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)
