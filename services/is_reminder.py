import re
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


def is_reminder_needed(user_prompt: str):
    prompt = f"""
Kullanıcının aşağıdaki komutuna göre bu TODO'nun zamanlı bir hatırlatma gerektirip gerektirmediğini değerlendir:

- Eğer kullanıcı ifadesinde belirli bir zaman, tarih, gün, saat gibi unsurlar varsa (örneğin: "yarın", "pazartesi", "09:00" gibi), bu bir hatırlatma gerektirir.
- Eğer belirli bir zaman belirtilmemişse ve yalnızca bir görev tanımı varsa, hatırlatmaya gerek yoktur.

Sadece aşağıdaki formatta cevap ver:

{{
  "reminder": true | false
}}

Kullanıcı komutu: "{user_prompt}"
"""
    response = llm.invoke(prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        return data.get("reminder", False)
    except Exception as e:
        raise ValueError(f"Yanıt ayrıştırılamadı: {e} | İçerik: {cleaned}")
