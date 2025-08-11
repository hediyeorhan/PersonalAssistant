from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import difflib
import os
from dotenv import load_dotenv
from typing import List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()

class DbInfoAgent:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("Database URL must be provided or set in environment variables")
        
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.session = None

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def debug_print_tables(self):
        """Tüm tabloları ve ilk 5 kaydı yazdır"""
        if not self.session:
            self.session = self.Session()
            
        print("\n🔍 VERİTABANI TABLOLARI VE İÇERİKLERİ:")
        for table_name in self.inspector.get_table_names():
            try:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                print(f"\n📋 TABLO: {table_name}")
                print("📝 Sütunlar:", [col.name for col in table.columns])
                
                # İlk 5 kaydı al
                result = self.session.execute(table.select().limit(100)).fetchall()
                if not result:
                    print("   ⚠️ Bu tablo boş")
                    continue
                    
                for i, row in enumerate(result, 1):
                    row_str = " | ".join(f"{col}:{getattr(row, col)}" for col in row._fields)
                    print(f"   {i}. {row_str}")
                    
            except SQLAlchemyError as e:
                print(f"⚠️ Tablo okunamadı: {table_name}, Hata: {e}")
            except Exception as e:
                print(f"⚠️ Beklenmeyen hata: {table_name}, Hata: {e}")

    def get_all_table_data(self) -> List[Tuple[str, str]]:
        all_data = []
        if not self.session:
            self.session = self.Session()
            
        for table_name in self.inspector.get_table_names():
            try:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                result = self.session.execute(table.select()).fetchall()
                
                for row in result:
                    row_str = " | ".join(f"{col}:{getattr(row, col)}" for col in row._fields)
                    all_data.append((table_name, row_str))
                    
            except SQLAlchemyError as e:
                print(f"⚠️ Tablo okunamadı: {table_name}, Hata: {e}")
            except Exception as e:
                print(f"⚠️ Beklenmeyen hata: {table_name}, Hata: {e}")
                
        return all_data

    def handle_prompt(self, prompt: str) -> str:
        prompt = prompt.lower()
        matches = []
        all_data = self.get_all_table_data()

        for table, row in all_data:
            try:
                score = difflib.SequenceMatcher(None, prompt, row.lower()).ratio()
                if score > 0.3:
                    matches.append((table, row, round(score, 2)))
            except Exception as e:
                print(f"⚠️ Karşılaştırma hatası: {e}")

        if not matches:
            return "❓ Bu soru veritabanıyla ilgili görünmüyor.\n" + \
                f"🔍 Veritabanında {len(all_data)} kayıt tarandı."

        matches.sort(key=lambda x: x[2], reverse=True)
        best_match = matches[0]
        
        # Gemini ile yorumlama
        try:
            llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))
            
            response = llm.invoke([
                SystemMessage(content="Sen bir veritabanı asistanısın. Kullanıcıya veritabanı kayıtlarını doğal dilde açıkla."),
                HumanMessage(content=f"""
                Kullanıcı sorusu: {prompt}
                Veritabanı kaydı (tablo: {best_match[0]}): {best_match[1]}

                Bu bilgiyi kullanarak kullanıcıya:
                1. Anlaşılır Türkçe cevap ver
                2. Sadece veritabanındaki bilgileri kullan. Veri tabanındaki bilgileri kullanıcıya güzel bir şekilde açıkla.
                3. Gereksiz detay ekleme
                4. Verinin nerede olduğu bilgisini verme o bilgiyi oradan al ve sen açıkla. Örneğin x ile ilgili bilgi x tablosunda var oradan erişebilirsiniz demek yerine veriyi çek ve sen açıkla!
                """)
            ])
            
            return f"📝 {response.content}\n"  # Kaynak veriyi kısalt
        except Exception as e:
            print(f"⚠️ Gemini hatası: {e}")
            return f"📊 Eşleşen kayıt (tablo: {best_match[0]}):\n➡️ {best_match[1]}"