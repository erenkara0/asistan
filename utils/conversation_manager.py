from typing import List
from langchain.schema import HumanMessage, AIMessage, BaseMessage

class ConversationManager:
    def __init__(self, max_history: int = 10):
        """
        Conversation history manager
        
        Args:
            max_history: Maximum number of message pairs to keep in memory
        """
        self.max_history = max_history
        self.history: List[BaseMessage] = []
    
    def add_user_message(self, message: str):
        """Kullanıcı mesajını geçmişe ekle"""
        self.history.append(HumanMessage(content=message))
        self._trim_history()
    
    def add_ai_message(self, message: str):
        """AI mesajını geçmişe ekle"""
        self.history.append(AIMessage(content=message))
        self._trim_history()
    
    def get_history(self) -> List[BaseMessage]:
        """Tüm geçmişi döndür"""
        return self.history.copy()
    
    def _trim_history(self):
        """Geçmişi belirtilen limite göre kırp"""
        if len(self.history) > self.max_history * 2:  # user + ai = 2 message per exchange
            # En eski mesaj çiftini kaldır
            self.history = self.history[2:] 