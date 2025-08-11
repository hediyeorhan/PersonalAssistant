from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tkinter as tk
from tkinter import messagebox
from services.reminder_llm_parser import parse_reminder_details_from_prompt, parse_prompt_to_action
from models.reminder_model import Reminder
import os
from services.send_mail import send_gmail


class ReminderAgent:
    def __init__(self):
        engine = create_engine(os.getenv("DATABASE_URL"))
        Session = sessionmaker(bind=engine)
        self.db = Session()
        
    def handle_prompt(self, prompt: str, extra_data=None):
        try:
            action_data = parse_prompt_to_action(prompt)
        except Exception as e:
            return f"❌ Komut çözümlenemedi: {e}"

        intent = action_data.get("intent")
        
        extra_data = extra_data or {}

        if intent == "add_reminder":
            try:
                parsed = parse_reminder_details_from_prompt(prompt)
                return self._add_reminder_from_parsed(parsed)
            except Exception as e:
                return f"❌ Hatırlatıcı eklenemedi: {e}" 

        elif intent == "get_all_reminder":
            return self._get_all_reminders()

        elif intent == "delete_reminder":
            id_list = None
            if extra_data and "id_list" in extra_data:
                id_list = extra_data["id_list"]
            else:
                return "⚠️ Hatırlatıcı id'leri belirtilmedi."
            return self._delete_reminder_by_id(id_list)

        return "❓ Komut anlaşılamadı."
    
    def _delete_reminder_by_id(self, id_list: list):
        deleted = []
        not_found = []

        for reminder_id in id_list:
            reminder = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
            if reminder:
                self.db.delete(reminder)
                deleted.append(f"{reminder_id}: {reminder.message}")
            else:
                not_found.append(str(reminder_id))

        self.db.commit()

        result = ""
        if deleted:
            result += "🗑️ Silinen hatırlatıcı(lar):\n" + "\n".join(deleted)
        if not_found:
            result += "\n⚠️ Bulunamayan id(ler): " + ", ".join(not_found)

        return result.strip()

        
    def _add_reminder_from_parsed(self, parsed_data: dict):
        try:
            new_reminder = Reminder(
                message=parsed_data["message"],
                remind_at=parsed_data["remind_at"],
                is_sent=False,
                created_at=datetime.now()
            )
            self.db.add(new_reminder)
            self.db.commit()
            self.db.refresh(new_reminder)
            return f"✅ Hatırlatıcı eklendi: {new_reminder.message} ({new_reminder.remind_at})"
        except Exception as e:
            return f"❌ Hatırlatıcı eklenemedi: {e}" 
        
    def _get_all_reminders(self):
        reminders = self.db.query(Reminder).order_by(Reminder.remind_at).all()
        if not reminders:
            return "📭 Hiç hatırlatıcı bulunamadı."
        return "\n".join([f"{r.id}. {r.message} - {'✅' if r.is_sent else '❌'} - {r.remind_at.strftime('%Y-%m-%d %H:%M')}" for r in reminders])
    

    def show_reminder_popup(self, message):
        root = tk.Tk()
        root.withdraw()  # Ana pencereyi gizle
        messagebox.showinfo("Hatırlatma", message)
        root.destroy()
        
        
    def get_today_reminders(self):
        now = datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        reminders = self.db.query(Reminder)\
            .filter(Reminder.remind_at >= now, Reminder.remind_at <= end_of_day)\
            .order_by(Reminder.remind_at.asc())\
            .all()
        return reminders
        

    def check_and_notify(self):
        try:
            now = datetime.now()
            reminder_window_start = now
            reminder_window_end = now + timedelta(minutes=15)
            subject = "Hatırlatma Mesajı"
            body = "Bu bir hatırlatma mesajıdır."
            messages = []

            print(f"[INFO] Şu anki zaman: {now}")

            # 15 dakika içinde olacak ve henüz gösterilmemiş hatırlatmalar
            try:
                reminders_to_notify = self.db.query(Reminder).filter(
                    Reminder.remind_at >= reminder_window_start,
                    Reminder.remind_at <= reminder_window_end,
                    Reminder.is_sent == False
                ).all()
                print(f"[INFO] Bulunan hatırlatma sayısı: {len(reminders_to_notify)}")
            except Exception as e:
                print(f"[ERROR] Hatırlatma sorgusunda hata: {e}")
                return

            if reminders_to_notify:
                for reminder in reminders_to_notify:
                    try:
                        message_text = f"- {reminder.message}\n\tHatırlatma saati: {reminder.remind_at.strftime('%Y-%m-%d %H:%M')}"
                        messages.append(message_text)
                        print(f"[NOTIFY] Gösterilen hatırlatma: {message_text}")
                        self.show_reminder_popup(message_text)  # Kullanıcı "Tamam" demeden ilerlemez
                        reminder.is_sent = True
                        self.db.commit()
                    except Exception as e:
                        print(f"[ERROR] Hatırlatma işleme hatası: {e}")

                subject = "🔔 Yeni Hatırlatma"
                body = "Aşağıdaki hatırlatmalarınız var:\n\n" + "\n".join(messages)

                try:
                    send_gmail(subject, body)
                    print("[INFO] E-posta gönderildi.")
                except Exception as e:
                    print(f"[ERROR] E-posta gönderimi başarısız: {e}")
            else:
                print("[INFO] Gösterilecek hatırlatma bulunamadı.")

            # Süresi geçmiş ama hâlâ is_sent = False olanları da işaretle
            try:
                expired_unseen_reminders = self.db.query(Reminder).filter(
                    Reminder.remind_at < now,
                    Reminder.is_sent == False
                ).all()
                print(f"[INFO] Kaçırılmış hatırlatma sayısı: {len(expired_unseen_reminders)}")
            except Exception as e:
                print(f"[ERROR] Kaçırılmış hatırlatma sorgusu hatası: {e}")
                return

            for reminder in expired_unseen_reminders:
                try:
                    print(f"[MARK] Kaçırılan hatırlatma işaretleniyor: {reminder.message}")
                    reminder.is_sent = True
                    self.db.commit()
                except Exception as e:
                    print(f"[ERROR] Kaçırılan hatırlatma işaretleme hatası: {e}")

        except Exception as general_error:
            print(f"[FATAL ERROR] check_and_notify genel hata: {general_error}")
