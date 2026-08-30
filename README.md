# Otel Problem Analiz Asistanı

Butik otellere müşteri kayıt yazılımı sağlayan bir şirket için geliştirilmiş, doğal dille sorgulanabilen problem analiz asistanı.

Destek ekibine gelen otel problemleri ve bunlara uygulanan çözümler bir PostgreSQL veritabanında birikiyor. Bu asistan, çalışanın "Geçen ay X otelinde hangi sorunlar çıkmış?" gibi serbest metinle yazdığı bir soruyu alıp arka planda ilgili kayıtları çekiyor ve özetleyerek cevaplıyor.

Amaç, ekibe yeni katılan bir çalışanın geçmiş çözümlere kıdemli birine sormadan ulaşabilmesiydi.

## Nasıl Çalışıyor

Klasik bir sohbet botundan farklı olarak model, cevabı kendi genel bilgisinden üretmiyor. Akış şöyle:

1. Kullanıcı serbest metinle sorusunu yazıyor.
2. Girdi, güvenlik doğrulamasından geçiyor (boş mesaj, uzunluk sınırı, içerik filtresi).
3. Mesaja güncel tarih/saat bilgisi ekleniyor — böylece model "geçen hafta", "bu ay" gibi göreli ifadeleri çözebiliyor.
4. LangChain'in tool calling mekanizmasıyla model, cümleden **otel adı**, **başlangıç tarihi**, **bitiş tarihi** ve **kayıt limiti** parametrelerini kendisi çıkarıp `otel_problem_analiz` aracını çağırıyor.
5. Araç, bu parametrelerle PostgreSQL'e filtreli ve sıralı bir sorgu atıyor.
6. Dönen kayıtlar modele bağlam olarak veriliyor ve model bunları özetleyerek cevabı üretiyor.

Bu sayede cevaplar genel geçer değil, veritabanındaki gerçek kayıtlara dayanıyor.

## Özellikler

- **Doğal dille sorgulama** — otel adı ve tarih aralığı filtrelerinin cümleden otomatik çıkarılması
- **Konuşma hafızası** — son 10 mesaj çifti tutuluyor, takip soruları önceki bağlamı dikkate alıyor
- **İki cevap modu** — normal ve token bazlı akış (streaming); `/stream` ve `/normal` komutlarıyla geçiş
- **Zaman farkındalığı** — göreli tarih ifadelerinin çözümlenmesi
- **Güvenlik katmanı** — girdi uzunluğu sınırı, boş mesaj kontrolü, içerik filtresi
- **Merkezî loglama** — konsol, dosya ve ayrı hata log dosyası
- **Graceful shutdown** — SIGINT/SIGTERM sinyallerinde veritabanı bağlantılarının temiz kapatılması

## Veritabanı Tasarımı

Kayıtlar `otel_data` tablosunda, Tortoise ORM modeli üzerinden yönetiliyor.

| Alan | Tip | Not |
|---|---|---|
| `id` | Integer | Birincil anahtar |
| `otel_ad` | CharField(100) | İndeksli |
| `departman` | CharField(100) | İndeksli |
| `problem_type` | CharField(100) | İndeksli |
| `aciklama` | Text | Problemin açıklaması |
| `cozum_oneri` | Text | Uygulanan çözüm |
| `created_at` | Datetime | İndeksli |

Sık kullanılan sorgu kalıpları için iki bileşik indeks tanımlı: `(otel_ad, created_at)` ve `(departman, problem_type)`. Varsayılan sıralama `-created_at` — yeni kayıtlar önce geliyor.

### Performans önlemleri

- Asenkron bağlantı havuzu (yapılandırılabilir min/max bağlantı sayısı)
- Bağlantı ve sorgu zaman aşımı ayarları
- Boşta kalan bağlantıların 5 dakika sonra kapatılması
- Sorgu başına maksimum kayıt limiti (varsayılan 50, tavan 500) — büyük sonuç kümelerinde bellek şişmesini önlemek için
- Sorgularda yalnızca ihtiyaç duyulan alanların çekilmesi

## Kullanılan Teknolojiler

- **Python** (asyncio tabanlı asenkron mimari)
- **LangChain** — `StructuredTool`, `bind_tools`, mesaj yönetimi
- **OpenAI API** — GPT-4.1
- **PostgreSQL** + **Tortoise ORM** (asyncpg sürücüsü)
- **Pydantic** — araç parametrelerinin şema doğrulaması
- **python-dotenv** — ortam değişkeni yönetimi

## Proje Yapısı

```
asistan/
├── main.py                          # CLI giriş noktası, ana döngü, signal handler'lar
├── agent.py                         # LangChain agent; normal ve streaming çalıştırma
├── config.py                        # Ortam değişkeni tabanlı yapılandırma
├── db.py                            # Tortoise ORM başlatma ve kapatma
├── models/
│   └── hotel_problem.py             # Veri modeli, indeksler
├── tools/
│   └── analysis_tool.py             # Filtreli sorgu aracı
├── security/
│   └── security_validator.py        # Girdi doğrulama
├── constants/
│   └── prompt_constants.py          # Sistem promptu ve hata mesajları
└── utils/
    ├── conversation_manager.py      # Konuşma geçmişi yönetimi
    ├── logger.py                    # Singleton logger
    └── time_utils.py                # Güncel zaman bilgisi
```

## Kurulum

```bash
git clone https://github.com/erenkara0/asistan.git
cd asistan
pip install -r requirements.txt
```

Proje kökünde bir `.env` dosyası oluşturun:

```
OPENAI_API_KEY=your_api_key_here

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hotel_analytics

DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT=30
DB_COMMAND_TIMEOUT=60

APP_ENV=development
LOG_LEVEL=INFO
MAX_QUERY_RESULTS=500
MAX_MESSAGE_LENGTH=1000
```

Çalıştırmak için:

```bash
python main.py
```

## Kullanım

```
💬 Siz: Grand Hotel'de geçen ay hangi problemler yaşandı?
🤖 Agent: Toplam 12 kayıt bulundu...

💬 Siz: /stream
✅ Streaming mode aktif

💬 Siz: quit
```

## Notlar

Proje, bir şirket için tam zamanlı çalışılan dönemde geliştirilmiştir. Gerçek API anahtarları ve veritabanı bilgileri yalnızca yerel `.env` dosyasında tutulur, repoya dahil edilmez.
