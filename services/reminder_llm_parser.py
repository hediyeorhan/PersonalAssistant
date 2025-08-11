import re
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

today = datetime.today().strftime("%Y-%m-%d")


def parse_reminder_details_from_prompt(user_prompt: str):
    prompt = f"""
Kullanıcının hatırlatma isteğini analiz et ve sadece aşağıdaki yapıda geçerli bir JSON üret:

{{
  "message": "Hatırlatmanın kısa ve öz başlığı",
  "remind_at": Hatırlatmanın tarihi ve saati. Format şu şekilde olmalı: "YYYY-MM-DD HH:MM:SS" (örneğin: "2024-05-27 14:00:00")
}}

Kurallar:
    - Eğer kullanıcı saati açıkça belirtmişse (örneğin "öğlen 2", "sabah 9", "akşam 6" gibi), bunu tanıyıp doğru saate dönüştür.
    - Eğer saat belirtilmemişse, varsayılan olarak "09:00:00" (sabah 9) olarak ayarla.

    Tarih kısmı için:
    - "bugün" denmişse, bugünün tarihi: "{today}"
    - "yarın" denmişse, bugünün tarihinin bir gün sonrası

    Sadece geçerli bir JSON çıktısı üret. Kod bloğu (```json gibi) ya da açıklama yazma.

### Örnekler:
    Kullanıcı: "Yarın sabah buzluktan et çıkar."
    Çıktı: {{
    "message": "Buzluktan et çıkar",
    "remind_at": "YYYY-MM-DD HH:MM:SS"  ← (doğru tarihi ve saati koy)
    }}

    Kullanıcı: "Cumartesi günü öğlen 4'te otogara gitmek için hazırlan"
    Çıktı: {{
    "message": "Otogara gitmek için hazırlan",
    "remind_at": "YYYY-MM-DD HH:MM:SS"  ← (doğru tarihi ve saati koy)

    }}


Kullanıcı ifadesi: "{user_prompt}"
"""
    response = llm.invoke(prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def parse_prompt_to_action(user_prompt: str):
    system_prompt = f"""Sen bir hatırlatıcısın. Kullanıcıdan gelen komutu analiz ederek, şu yapıda JSON üret:

    {{
    "intent": "add_reminder" | "get_all_reminder" | "delete_reminder",
    "parameters": {{
        // intent'e bağlı parametreler
    }}
    }}

    Bazı örnekler:
    - 'Yarın saat 3'te marketten süt alınacak' → add_reminder
    - 'Toplantı notlarını tamamla' → add_reminder
    - 'Yarın temizlik yapılacak' → add_reminder
    - 'Tüm görevleri listele' → get_all_reminder
    - 'Yapılacaklar neler' → get_all_reminder
    - 'toplantı notları alındı sil' → delete_reminder
    - 'yarınki görevleri sil' → delete_reminder
    

    Kullanıcı ifadesi: "{user_prompt}"
    """
    
    response = llm.invoke(system_prompt)
    content = response.content.strip()  # Gemini'nin döndürdüğü yanıt
    cleaned = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        return data
    except Exception as e:
        raise ValueError(f"JSON parse hatası: {e} | Yanıt: {cleaned}")

