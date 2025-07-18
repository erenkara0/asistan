from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
from models.hotel_problem import HotelProblem
from datetime import datetime
from utils.logger import Logger
from config import config

# Logger'ı initialize et
logger = Logger.get_logger("analysis_tool")

class AnalysisInput(BaseModel):
    otel_ad: Optional[str] = Field(None, description="Otelin adı (opsiyonel)")
    start_date: Optional[str] = Field(None, description="Başlangıç tarihi (YYYY-MM-DD, opsiyonel)")
    end_date: Optional[str] = Field(None, description="Bitiş tarihi (YYYY-MM-DD, opsiyonel)")
    limit: Optional[int] = Field(50, description=f"Maksimum kayıt sayısı (varsayılan: 50, max: {config.MAX_QUERY_RESULTS})")

async def analyze_problems(
    otel_ad: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 50
) -> str:
    # Limit kontrolü - memory patlamasını önlemek için
    if limit is None or limit <= 0:
        limit = 50
    elif limit > config.MAX_QUERY_RESULTS:
        limit = config.MAX_QUERY_RESULTS  # Config'den max limit al
    
    # Query builder - optimized
    query = HotelProblem.filter()  # all() yerine filter() kullan
    
    # Filtreler - indexli alanları kullan
    if otel_ad:
        # Büyük küçük harf duyarsız tam eşleşme (indexli)
        query = query.filter(otel_ad__iexact=otel_ad)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(created_at__gte=start_dt)
        except Exception as e:
            logger.error(f"Başlangıç tarihi parse hatası: {start_date}, hata: {str(e)}")
            return "Başlangıç tarihi formatı yanlış. 'YYYY-MM-DD' biçiminde olmalı."
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(created_at__lte=end_dt)
        except Exception as e:
            logger.error(f"Bitiş tarihi parse hatası: {end_date}, hata: {str(e)}")
            return "Bitiş tarihi formatı yanlış. 'YYYY-MM-DD' biçiminde olmalı."
    
    try:
        # Performance: Sadece gerekli alanları al + sıralı + limit
        results = await query.order_by('-created_at').limit(limit).values(
            'id', 'otel_ad', 'departman', 'problem_type', 'aciklama', 'created_at'
        )
        
        # Toplam kayıt sayısını da al (pagination bilgisi için)
        total_count = await query.count()
        
    except Exception as e:
        logger.error(f"Veritabanı sorgusu hatası: {str(e)}", exc_info=True)
        return "Veritabanı sorgusu sırasında bir hata oluştu."

    if not results:
        return "Kriterlere uygun herhangi bir problem kaydı bulunamadı."

    # Response oluştur
    response = f"Toplam {total_count} kayıt bulundu"
    
    if total_count > limit:
        response += f" (İlk {limit} kayıt gösteriliyor)"
    
    response += ".\n\n"
    
    # Sonuçları formatla
    for r in results:
        # created_at dictionary'den datetime objesine çevir
        created_date = r['created_at'].date() if isinstance(r['created_at'], datetime) else r['created_at']
        response += f"- [{created_date}] {r['otel_ad']} | {r['problem_type']}: {r['aciklama']}\n"
    
    # Eğer daha fazla kayıt varsa bilgi ver
    if total_count > limit:
        response += f"\n💡 Daha fazla kayıt için filtreleme yapın veya limit artırın (max: {config.MAX_QUERY_RESULTS})."
    
    return response

analysis_tool = StructuredTool.from_function(
    name="otel_problem_analiz",
    description=f"Otel adı ve/veya tarih aralığına göre problem kayıtlarını analiz eder. Performans için max {config.MAX_QUERY_RESULTS} kayıt döndürür.",
    func=analyze_problems,
    args_schema=AnalysisInput,
    coroutine=analyze_problems 
)