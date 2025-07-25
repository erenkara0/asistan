from tortoise import fields
from tortoise.models import Model

class HotelProblem(Model):
    id = fields.IntField(pk=True)
    otel_ad = fields.CharField(max_length=100, index=True)  
    departman = fields.CharField(max_length=100, index=True)  
    problem_type = fields.CharField(max_length=100, index=True) 
    aciklama = fields.TextField(null=True)
    cozum_oneri = fields.TextField(null=True)
    created_at = fields.DatetimeField(index=True)  

    class Meta:
        table = "otel_data"  # PostgreSQL'deki tablo ismi
        # Composite index - sık kullanılan sorgu kombinasyonları için
        indexes = [
            # Otel adı + tarih kombinasyonu için
            ["otel_ad", "created_at"],
            # Departman + problem tipi kombinasyonu için
            ["departman", "problem_type"]
        ]
        # Sıralama performansı için
        ordering = ["-created_at"]  # Yeni kayıtlar önce

    def __str__(self):
        return f"{self.otel_ad} - {self.problem_type} - {self.created_at}"