# constants/prompt_constants.py

def time_info_template(time_info: dict, user_message: str) -> str:
    return (
        f"🕒 Şu an: {time_info['datetime']} ({time_info['weekday']})\n"
        f"Kullanıcı mesajı: {user_message}\n"
        "Bu bilgilere göre yanıt ver."
    )

SYSTEM_DIRECTIVE = """
Sen bir otel problem analiz asistanısın. Kullanıcıdan gelen mesajlara göre, otel problemleri veritabanından ilgili kayıtları bulur, özetler ve sade bir şekilde rapor edersin.
Eğer kullanıcı otel adı veya tarih aralığı belirtirse, buna uygun analiz yaparsın.
Cevaplarında kısa ve net ol, gereksiz tekrar yapma.
Eğer veri yoksa kibarca bildir.
"""

SYSTEM_PROMPTS = {
    "SYSTEM_DIRECTIVE": SYSTEM_DIRECTIVE,
    "TIME_INFO_TEMPLATE": time_info_template
}

ERROR_MESSAGES = {
    "NO_RESPONSE": "Üzgünüm, bir yanıt oluşturulamadı.",
    "GENERAL_ERROR": lambda detail="": f"Bir hata oluştu: {detail}"
}
