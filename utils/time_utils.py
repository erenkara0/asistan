from datetime import datetime
import locale

class TimeUtils:

    @staticmethod
    def get_current_time_info():
        # Türkçe gün isimleri için locale ayarla (Windows'ta çalışmayabilir)
        try:
            locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
        except locale.Error:
            pass  # Eğer sistemde Türkçe locale yoksa default kullanılır

        now = datetime.now()

        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),  # Türkçe olması locale'a bağlı
            "hour": now.hour,
            "minute": now.minute,
        }
