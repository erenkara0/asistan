import re
from config import config

class SecurityValidator:
    BLACKLISTED_WORDS = [
        "hack", "kill", "bomb", "terror", "virus", "porn", "exploit"
    ]

    @staticmethod
    def validate_request(message: str) -> dict:
        # Boş mesaj kontrolü
        if not message or not message.strip():
            return {
                "is_valid": False,
                "error_message": "Boş mesaj gönderilemez."
            }

        # Uzunluk kontrolü
        if len(message) > config.MAX_MESSAGE_LENGTH:
            return {
                "is_valid": False,
                "error_message": "Mesaj çok uzun. Lütfen daha kısa bir mesaj yazın."
            }

        # Kara liste kontrolü
        lower_msg = message.lower()
        for word in SecurityValidator.BLACKLISTED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", lower_msg):
                return {
                    "is_valid": False,
                    "error_message": "Bu mesaj güvenlik politikalarımıza aykırıdır."
                }

        # Eğer tüm kontroller geçerse
        return {
            "is_valid": True,
            "error_message": None
        }
