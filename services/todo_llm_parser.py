from datetime import datetime
import re
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

today = datetime.today().strftime("%Y-%m-%d")

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

def parse_todo_from_prompt(user_prompt: str):

    prompt = f"""
    Aşağıdaki kullanıcı ifadesini analiz et ve sadece aşağıdaki yapıda geçerli bir JSON üret:

    - "title": Görevin kısa ve öz başlığı.
    - "description": Görevin detaylı açıklaması. Yoksa title tekrarlanabilir.
    - "due_date": Görevin tarihi ve saati. Format şu şekilde olmalı: "YYYY-MM-DD HH:MM:SS" (örneğin: "2024-05-27 14:00:00")

    Kurallar:
    - Eğer kullanıcı saati açıkça belirtmişse (örneğin "öğlen 2", "sabah 9", "akşam 6" gibi), bunu tanıyıp doğru saate dönüştür.
    - Eğer saat belirtilmemişse, varsayılan olarak "09:00:00" (sabah 9) olarak ayarla.

    Tarih kısmı için:
    - "bugün" denmişse, bugünün tarihi: "{today}"
    - "yarın" denmişse, bugünün tarihinin bir gün sonrası

    Sadece geçerli bir JSON çıktısı üret. Kod bloğu (```json gibi) ya da açıklama yazma.

    ### Örnekler:
    Kullanıcı: "Yarın sabah sunum hazırlığını bitir."
    Çıktı: {{
    "title": "Sunum hazırlığını bitir",
    "description": "Yarın sabah sunum hazırlığının tamamlanması",
    "due_date": "YYYY-MM-DD HH:MM:SS"  ← (doğru tarihi ve saati koy)
    }}

    Kullanıcı: "Cumartesi günü öğlen 2'de sinema bileti al"
    Çıktı: {{
    "title": "Sinema bileti al",
    "description": "Cumartesi günü saat 14:00'te sinema bileti alınması",
    "due_date": "YYYY-MM-DD HH:MM:SS"  ← (doğru tarihi ve saati koy)

    }}

    Kullanıcı ifadesi: "{user_prompt}"
    """


    response = llm.invoke(prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        return data
    except Exception as e:
        raise ValueError(f"JSON parse hatası: {e} | Yanıt: {cleaned}")
    


def parse_prompt_to_action(user_prompt: str):
    system_prompt = f"""Sen bir görev yöneticisisin. Kullanıcıdan gelen komutu analiz ederek, şu yapıda JSON üret:

    {{
    "intent": "add_todo" | "get_all_todos" | "complete_todo" | "delete_todo",
    "parameters": {{
        // intent'e bağlı parametreler
    }}
    }}

    Bazı örnekler:
    - 'Yarın saat 3'te marketten süt alınacak' → add_todo
    - 'Toplantı notlarını tamamla' → add_todo
    - 'Yarın temizlik yapılacak' → add_todo
    - 'Tüm görevleri listele' → get_all_todos
    - 'Yapılacaklar neler' → get_all_todos
    - 'temizlik görevi tamamlandı' → complete_todo
    - 'ekmek alındı' → complete_todo
    - 'bugünkü görevler tamamlandı' → complete_todo
    - 'toplantı notları alındı sil' → delete_todo
    - 'yarınki görevleri sil' → delete_todo
    

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

