import re
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

def parse_prompt_to_action(user_prompt: str):
    prompt = f"""
Kullanıcının aşağıdaki ifadesine göre bir komut belirle. Format şu şekilde olmalı:

{{
  "intent": "add_note" | "get_notes" | "delete_note",
}}

Örnekler:
- "Yeni bir not oluştur: alışveriş listesi" → add_note
- "Alınacaklar şunlar" → add_note
- "Pazartesi Ankaraya gideceğim için öncesinde belki dedemi ziyaret ederim" → add_note
- "Notları göster" → get_notes
- "Notlarım" → get_notes
- "Tüm notlarım" → get_notes
- "Notlarım neler" → get_notes
- "3 numaralı notu sil" → delete_note
- "X notunu kaldır" → delete_note


Kullanıcı ifadesi: "{user_prompt}"
    """
    response = llm.invoke(prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def parse_note_from_prompt(user_prompt: str):
    prompt = f"""
Kullanıcının not isteğini analiz et ve aşağıdaki formatta bir JSON oluştur:

{{
  "title": "Not başlığı",
  "content": "Not içeriği"
}}

Kullanıcı ifadesi: "{user_prompt}"
    """
    response = llm.invoke(prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
    return json.loads(cleaned)
