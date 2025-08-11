# Personal Assistant with MultiAgent

Bu çalışmada Google AI tarafından geliştirilen yapay zekâ Gemini API'ı kullanılarak bir kişisel asistan projesi geliştirilmiştir. Projede multiagent yapılar kullanılmıştır. Kullanıcıdan alınan girdinin not mu, todo mu, hatırlatıcı mı olduğunu llm kendisi tanımlı promptları ile belirlemektedir. Karar verdikten sonra veri tabanı ile etkileşime girerek görevlerini yerine getirmektedir. Projede multiagent yapısı router ve promptlar ile yönetilmiştir.

Projede __.env__ dosyasında içeriğinde şu veriler bulunmaktadır.

• GEMINI_API_KEY=

• HOST=

• PORT= 

• DB_NAME=

• USER=

• PASSWORD=

• DATABASE_URL=

• GOOGLE_API_KEY=

• GEMINI_MODEL=

• mail_password=

• to_email=

• mail_username=

Projede, Gemini AI ile birlikte multiagent bir yapı kullanılmıştır. Multiagent bir yapı kullanılarak farklı özellikler/görevler kazandırılmıştır. Projede dört adet agent bulunmaktadır.

• db_info= Veri tabanında bulunan verileri çekerek kullanıcının sorusuna uygun bir bilgi varsa cevap vermektedir.

• note= Kullanıcının girmek istediği notları veri tabanında bulunan not tablosuna eklemektedir. Notları listeleme, silme ve ekleme görevleri vardır.

• reminder= Kullanıcının girmek istediği hatırlatıcıları veri tabanında bulunan tabloya eklemektedir. Hatırlatıcıları listeleme, silme ve ekleme görevleri vardır. Hatırlatıcı ekleme kısmı todo agent içerisinde çağırılmaktadır.

• todo= Kullanıcın todo listesine eklemek istediklerini kaydetmektedir. Eğer tarih ve saat verileri varsa bunu hatırlatıcı olarak da eklemek isteyip istemediğini kullanıcıya sorarak ekleme yapmaktadır. Todo listesindeki görevleri tamamlandı olarak işaretleme, todo silme, todo listeleme ve todo ekleme görevleri vardır.

Ek olarak projede reminder için yazılan bazı hizmetler mevcuttur. Kullanıcının hatırlatıcı olarak eklediği veriler 15 dk kaldığında kullanıcıya hatırlatılmaktadır. Bunun için Windows işletim sisteminde bulunan Task Scheduler kullanılmıştır. Burada bir task planlanmıştır ve 5 dk aralıklar ile çalışmaktadır. Veri tabanına eklenen bir hatırlatıcının gerçekleşmesine 15 dakikadan az bir süre kaldığında ekrana bir uyaır kutusu çıkarmaktadır ve kullanıcıya mail ile hatırlatma yapmaktadır. 5 dk aralıklar ile sürekli çalışmaktadır. 

Task Scheduler ile çalışan hatırlatıcı servisinin ekrana uyarı olarak gelen çıktı örneği Şekil 1'de görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/32c266f0-656d-43c5-801c-b4a129102cde" alt="image">
</div>
Şekil 1. Hatırlatıcı ekran uyarısı
<br>
<br>

Task Scheduler ile çalışan hatırlatıcı servisinin mail adresine hatırlatma olarak gelen çıktı örneği Şekil 2'de görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/484c0d8e-7c3f-4736-a8cf-1f0ceff32298" alt="image">
</div>
Şekil 2. Hatırlatıcı mail uyarısı
<br>
<br>

Veri tabanından kullanıcının sorduğu soruya uygun bilgileri çeken ve getiren db_info agent örnek çıktısı Şekil 3'te görülmektedir. Aranan veri ile ilgili sonuç veri tabanında bulunmadığı durumlarda ise örnek çıktı Şekil 4'te görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/8daf5437-fcd0-44e1-9616-dbcd094b8477" alt="image">
</div>
Şekil 3. Db_info agent örnek çıktısı
<br>
<br>

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/abbf0561-39bc-492d-aaad-c100ceb7624a" alt="image">
</div>
Şekil 4. Db_info agent örnek çıktısı - veri bulunamadığı durumlar
<br>
<br>

Kullanıcı bir todo eklemek istediğinde kod içerisinde kullanıcı isteği değerlendirilmektedir. Gerekli görülürse kullanıcıya hatırlatıcı eklemek ister misiniz şeklinde sorulmaktadır. Örnek çıktı Şekil 5'te görülmektedir.
Hatırlatma tarihi/saati yaklaşan hatırlatmalar arayüz üzerinde yan panelde görülmektedir. Yakın tarihli yeni bir hatırlatıcı eklendiğinde panel kendini güncellemektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/426b9b97-654a-4fc5-8512-940b323069a3" alt="image">
</div>
Şekil 5. Kullanıcıya hatırlatıcı olarak ekleme isteğinin sorulması
<br>
<br>

Hatırlatıcı ve todo verilerinin eklenmesi ile ilgili örnek çıktı Şekil 6'da görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/1a5cc83a-c661-4418-a4fe-4730481ee3ea" alt="image">
</div>
Şekil 6. Hatırlatıcı ve todo verilerinin eklenmesi
<br>
<br>

Not, hatırlatıcı ve todo listelerinde tamamlandı olarak işaretlenen veriler ve silinmek istenen veriler sırası ile , konularak girilebilmektedir. Örnek çıktı Şekil 7'de görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/e315fe51-35f6-4f10-991f-93d6b88a1617" alt="image">
</div>
Şekil 7. Silinmek ve tamamlanmak istenen verilerin iletilmesi
<br>
<br>


Görevlerin silinmesinin ardından sistemden gelen cevap örnek çıktısı Şekil 8'de görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/b15da08f-5706-4888-8054-b7c1f49e3819" alt="image">
</div>
Şekil 8. Örnek agent çıktısı
<br>
<br>

Hatırlatıcı eklemek istenilmediği durumlarda ise örnek çıktı Şekil 9'da görülmektedir.

<br>
<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/59fba6fc-59f7-419f-bf6c-c808fda9b4a9" alt="image">
</div>
Şekil 9. Örnek agent çıktısı
<br>
<br>