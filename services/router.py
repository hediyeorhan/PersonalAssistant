from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

def classify_agent(user_prompt: str):
    system_prompt = f"""
Sen bir komut sınıflandırıcısın. Kullanıcıdan gelen komutu analiz et ve bunun bir görev (TODO) mü yoksa bir not (NOTE) mu yoksa bir hatırlatıcı (REMINDER) mı yoksa bir (DB_INFO) mu olduğunu belirle.

Aşağıdaki kurallara göre karar ver:

- Eğer komut bir eylem içeriyor, belirli bir zaman/tarih içeriyorsa veya yapılması gereken bir şeyi ifade ediyorsa: `"todo"`
- Eğer komut daha çok bir fikir, liste, bilgi notu ya da açıklama içeriyorsa: `"note"`
- Komutta belirli bir eylem varsa (örneğin: al, yap, git, temizle, gönder gibi), bu bir "todo" görevidir.
- Komut bir zaman/tarih içeriyorsa (örneğin: yarın, pazartesi, saat 9'da), bu da "todo" olabilir.
- Komut bilgi verme amaçlıysa (örneğin: market listesi, proje notları, yapılacakların özeti gibi) bu bir "note"tur.
- Hatırlatıcı silmek istiyorum derse, bu bir "reminder" işlemidir.
- Hatırlatıcılarımı listele derse, bu bir "reminder" işlemidir.
- Uyarı silmek istiyorum derse, bu bir "reminder" işlemidir.
- Uyarılarımı listele derse, bu bir "reminder" işlemidir.
- Yapacağım işleri listele derse, bu bir "todo" görevidir.
- Görevlerim neler derse, bu bir "todo" görevidir.
- Eğer komut bir veritabanı durumu, sorgusu ya da tablo/kolon bilgisi içeriyorsa bu bir "db_info" görevidir.
- Veritabanındaki verileri içeren spesifik sorular var ise bu bir "db_info" görevidir.
- Nasıl yapılır? Nedir? Bilgi verir misin gibi sorular var ise bu bir "db_info" görevidir.

Örnekler:

- "Yarın saat 3'te sunum yapacağım" → todo
- "Bugün alışveriş listesi: süt, yumurta, peynir" → note
- "Hoca dönüş yaptıktan sonra kodu güncelle" → todo
- "Tez çalışması için önemli notlar: literatür eksik" → note
- "Pazartesi saat 10:00'da müşteri toplantısı var" → todo
- "Toplantı notları: müşteri testten memnun değil" → note
- "Akşam 8’de maç izlenecek" → todo
- "Yeni hedefler: 1) veri analizi 2) test planı oluşturma" → note
- Hatırlatıcı listele → reminder
- Hatırlatıcı sil → reminder
- Hatırlatıcılarım neler → reminder
- Uyarı sil → reminder
- Uyarıları listele → reminder
- Görevlerim neler → todo
- Yapacağım işleri listele → todo
- Notlarımı söyler misin → note
- Yapacaklarımı söyler misin → todo
- X toplantısı saat kaçta → db_info
- Alışveriş listemde neler var dediğinde → "db_info"
- Cumartesi kod kaçta tetiklenecek → "db_info"
- X nedir? → "db_info"
- X hakkında bilgi verir misin? → "db_info"



Cevabı sadece aşağıdaki formatta ver:
{{
  "agent": "todo" | "note" | "reminder" | "db_info"
}}

Kullanıcı komutu: "{user_prompt}"
"""

    response = llm.invoke(system_prompt)
    content = response.content.strip()
    cleaned = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        return data.get("agent", "unknown")
    except Exception as e:
        raise ValueError(f"Yanıt ayrıştırılamadı: {e} | İçerik: {cleaned}")


