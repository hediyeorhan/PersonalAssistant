from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.todo_model import Todo
from datetime import datetime, timedelta
from services.todo_llm_parser import parse_todo_from_prompt, parse_prompt_to_action
import os
from dotenv import load_dotenv
from services.is_reminder import is_reminder_needed 
from services.reminder_llm_parser import parse_reminder_details_from_prompt
from agents.reminder_agent import ReminderAgent


load_dotenv()

class TodoAgent:
    def __init__(self):
        engine = create_engine(os.getenv("DATABASE_URL"))
        Session = sessionmaker(bind=engine)
        self.db = Session()
        self.reminder = ReminderAgent()

    def handle_prompt(self, prompt: str, extra_data=None):
        try:
            action_data = parse_prompt_to_action(prompt)
        except Exception as e:
            return f"❌ Komut çözümlenemedi: {e}"

        intent = action_data.get("intent")
        
        extra_data = extra_data or {}

        if intent == "add_todo":
            try:
                
                if is_reminder_needed(prompt):
                    reminder_confirm = extra_data.get("reminder_confirm")

                    if reminder_confirm is None:
                        # Frontend henüz karar vermedi, hatırlatma iste
                        return "Hatırlatma ister misiniz? (Evet/Hayır)"
                    elif reminder_confirm:  # True ise
                        parsed_reminder = parse_reminder_details_from_prompt(prompt)
                        self.reminder._add_reminder_from_parsed(parsed_reminder)
                        
                        parsed = parse_todo_from_prompt(prompt)
                        todo_result = self._add_todo_from_parsed(parsed)
                        
                        return f"{todo_result}\n✅ Hatırlatma eklendi."
                    else:
                        parsed = parse_todo_from_prompt(prompt)
                        todo_result = self._add_todo_from_parsed(parsed)
                        
                        return f"{todo_result}\n❌ Hatırlatma eklenmedi."
                
                else:
                    # Hatırlatma gerekmiyorsa direkt ekle
                    parsed = parse_todo_from_prompt(prompt)
                    return self._add_todo_from_parsed(parsed)

            except Exception as e:
                return f"❌ Görev eklenemedi: {e}"


        elif intent == "get_all_todos":
            return self._get_all_todos()

        elif intent == "complete_todo":
            id_list = None
            if extra_data and "id_list" in extra_data:
                id_list = extra_data["id_list"]
            else:
                return "⚠️ Görev id'leri belirtilmedi."
            return self._handle_complete_or_delete(prompt, action_data, id_list, complete=True)

        elif intent == "delete_todo":
            id_list = None
            if extra_data and "id_list" in extra_data:
                id_list = extra_data["id_list"]
            else:
                return "⚠️ Silinecek görev id'leri belirtilmedi."
            return self._handle_complete_or_delete(prompt, action_data, id_list, complete=False)


        return "❓ Komut anlaşılamadı."

    def _handle_complete_or_delete(self, prompt: str, action_data: dict, id_list, complete=True):
        
        try:
            return self._complete_todo_by_id(id_list) if complete else self._delete_todo_by_id(id_list)
        except:
            return "⚠️ Görev bilgisi eksik."

    def _add_todo_from_parsed(self, parsed_data: dict):
        
        try:
            new_todo = Todo(
                title=parsed_data["title"],
                description=parsed_data.get("description", parsed_data["title"]),
                due_date=parsed_data["due_date"],
                is_completed=False,
                created_at=datetime.now()
            )
            self.db.add(new_todo)
            self.db.commit()
            self.db.refresh(new_todo)
            return f"✅ Görev eklendi: {new_todo.title} ({new_todo.due_date})"
        except Exception as e:
            return f"❌ Görev eklenemedi: {e}" 

    def _get_all_todos(self):
        todos = self.db.query(Todo).order_by(Todo.due_date).all()
        if not todos:
            return "📭 Hiç görev bulunamadı."
        return "\n".join([f"{t.id}. {t.title} - {'✅' if t.is_completed else '❌'} - {t.due_date.strftime('%Y-%m-%d %H:%M')}" for t in todos])

    def _complete_todo_by_id(self, id_list: list):
        completed = []
        not_found = []

        for todo_id in id_list:
            todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
            if todo:
                todo.is_completed = True
                completed.append(f"{todo_id}: {todo.title}")
            else:
                not_found.append(str(todo_id))

        self.db.commit()

        result = ""
        if completed:
            result += "✅ Tamamlanan görev(ler):\n" + "\n".join(completed)
        if not_found:
            result += "\n⚠️ Bulunamayan id(ler): " + ", ".join(not_found)

        return result.strip()


    def _delete_todo_by_id(self, id_list: list):
        deleted = []
        not_found = []

        for todo_id in id_list:
            todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
            if todo:
                self.db.delete(todo)
                deleted.append(f"{todo_id}: {todo.title}")
            else:
                not_found.append(str(todo_id))

        self.db.commit()

        result = ""
        if deleted:
            result += "🗑️ Silinen görev(ler):\n" + "\n".join(deleted)
        if not_found:
            result += "\n⚠️ Bulunamayan id(ler): " + ", ".join(not_found)

        return result.strip()

