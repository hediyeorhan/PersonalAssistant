from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.note_model import Note
from services.note_llm_parser import parse_prompt_to_action, parse_note_from_prompt
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

class NoteAgent:
    def __init__(self):
        engine = create_engine(os.getenv("DATABASE_URL"))
        Session = sessionmaker(bind=engine)
        self.db = Session()

    def handle_prompt(self, prompt: str, extra_data=None):
        try:
            action_data = parse_prompt_to_action(prompt)
        except Exception as e:
            return f"Komut çözümlenemedi: {e}"

        intent = action_data.get("intent")
        
        extra_data = extra_data or {}

        if intent == "add_note":
            try:
                parsed = parse_note_from_prompt(prompt)
                return self._add_note(parsed)
            except Exception as e:
                return f"Not eklenemedi: {e}"

        elif intent == "get_notes":
            return self._get_all_notes()

        elif intent == "delete_note":
            id_list = None
            if extra_data and "id_list" in extra_data:
                id_list = extra_data["id_list"]
            else:
                return "⚠️ Silinecek not id'leri belirtilmedi."
            return self._delete_note_by_id(id_list)

    def _add_note(self, parsed):
        note = Note(
            title=parsed["title"],
            content=parsed["content"],
            created_at=datetime.now()
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return f"📝 Not eklendi: {note.title}"

    def _get_all_notes(self):
        notes = self.db.query(Note).order_by(Note.id.asc()).all()
        if not notes:
            return "Hiç not bulunamadı."
        return "\n".join([f"{n.id}. {n.title} - {n.created_at.strftime('%Y-%m-%d %H:%M')}\t\t -- {n.content}" for n in notes])

    def _delete_note_by_id(self, note_ids: list):
        deleted = []
        not_found = []

        for note_id in note_ids:
            note = self.db.query(Note).filter(Note.id == note_id).first()
            if note:
                self.db.delete(note)
                deleted.append(f"{note_id}: {note.title}")
            else:
                not_found.append(str(note_id))

        self.db.commit()

        result = ""
        if deleted:
            result += "🗑️ Silinen not(lar):\n" + "\n".join(deleted)
        if not_found:
            result += "\n⚠️ Bulunamayan id(ler): " + ", ".join(not_found)

        return result.strip()

