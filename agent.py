from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import ToolMessage
from tools.analysis_tool import analysis_tool
from constants.prompt_constants import SYSTEM_PROMPTS, ERROR_MESSAGES
from utils.time_utils import TimeUtils
from utils.logger import Logger
from utils.conversation_manager import ConversationManager
from typing import Optional

# Logger'ı initialize et
logger = Logger.get_logger("agent")

tools = [analysis_tool]

def create_agent(conversation_manager: Optional[ConversationManager] = None):
    model = ChatOpenAI(
        temperature=1,
        model="gpt-4.1"
    )
    llm_with_tools = model.bind_tools(tools)

    async def run(user_message: str) -> str:
        try:
            # Zaman bilgisini al
            time_info = TimeUtils.get_current_time_info()
            time_prompt = SYSTEM_PROMPTS["TIME_INFO_TEMPLATE"](time_info, user_message)

            # Base messages listesi
            messages = []
            messages.append(SystemMessage(content=SYSTEM_PROMPTS["SYSTEM_DIRECTIVE"]))
            
            # Conversation history'yi ekle
            if conversation_manager:
                history = conversation_manager.get_history()
                if history:
                    # Tüm history'yi ekle
                    messages.extend(history)
                    
            # Current message'ı ekle
            messages.append(HumanMessage(content=time_prompt))

            # AI modelini çağır
            ai_message = await llm_with_tools.ainvoke(messages)

            # Tool çağrısı olup olmadığını güvenli kontrol et
            tool_calls = getattr(ai_message, "tool_calls", None)
            if not tool_calls and hasattr(ai_message, "additional_kwargs"):
                tool_calls = ai_message.additional_kwargs.get("tool_calls")

            # Tool çağrısı yoksa direkt içerik döndür
            if not tool_calls:
                response_content = str(ai_message.content or ERROR_MESSAGES["NO_RESPONSE"])
                
                # User message ve AI cevabını conversation history'ye ekle
                if conversation_manager:
                    conversation_manager.add_user_message(user_message)
                    conversation_manager.add_ai_message(response_content)
                
                return response_content

            # Tool çağrısı varsa: Her bir tool_call için doğru ToolMessage oluştur
            tool_messages = []
            for tool_call in tool_calls:
                # tool_call["id"]: Tool çağrısı ID'si, tool_call["args"]: Tool fonksiyonu argümanları
                tool_result = await tools[0].ainvoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_result)
                    )
                )

            messages.append(ai_message)
            messages.extend(tool_messages)

            # Final yanıtı al
            final_response = await llm_with_tools.ainvoke(messages)
            response_content = str(final_response.content or ERROR_MESSAGES["NO_RESPONSE"])
            
            # User message ve AI cevabını conversation history'ye ekle
            if conversation_manager:
                conversation_manager.add_user_message(user_message)
                conversation_manager.add_ai_message(response_content)
            
            return response_content

        except Exception as e:
            logger.error(f"Agent hatası: {str(e)}", exc_info=True)
            return ERROR_MESSAGES["GENERAL_ERROR"](str(e))

    async def stream_run(user_message: str):
        """Streaming response - yields chunks as they come"""
        try:
            # Zaman bilgisini al
            time_info = TimeUtils.get_current_time_info()
            time_prompt = SYSTEM_PROMPTS["TIME_INFO_TEMPLATE"](time_info, user_message)

            # Base messages listesi
            messages = []
            messages.append(SystemMessage(content=SYSTEM_PROMPTS["SYSTEM_DIRECTIVE"]))
            
            # Conversation history'yi ekle
            if conversation_manager:
                history = conversation_manager.get_history()
                if history:
                    # Tüm history'yi ekle
                    messages.extend(history)
                    
            # Current message'ı ekle
            messages.append(HumanMessage(content=time_prompt))

            # AI modelini çağır
            ai_message = await llm_with_tools.ainvoke(messages)

            # Tool çağrısı olup olmadığını güvenli kontrol et
            tool_calls = getattr(ai_message, "tool_calls", None)
            if not tool_calls and hasattr(ai_message, "additional_kwargs"):
                tool_calls = ai_message.additional_kwargs.get("tool_calls")

            # Tool çağrısı yoksa direkt streaming yap
            if not tool_calls:
                response_content = ""
                async for chunk in llm_with_tools.astream(messages):
                    if chunk.content:
                        chunk_text = str(chunk.content)
                        response_content += chunk_text
                        yield chunk_text
                
                # User message ve AI cevabını conversation history'ye ekle
                if conversation_manager:
                    conversation_manager.add_user_message(user_message)
                    conversation_manager.add_ai_message(response_content)
                return

            # Tool çağrısı varsa: Her bir tool_call için doğru ToolMessage oluştur
            tool_messages = []
            for tool_call in tool_calls:
                tool_result = await tools[0].ainvoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_result)
                    )
                )

            messages.append(ai_message)
            messages.extend(tool_messages)

            # Final yanıtı streaming olarak al
            response_content = ""
            async for chunk in llm_with_tools.astream(messages):
                if chunk.content:
                    chunk_text = str(chunk.content)
                    response_content += chunk_text
                    yield chunk_text
            
            # User message ve AI cevabını conversation history'ye ekle
            if conversation_manager:
                conversation_manager.add_user_message(user_message)
                conversation_manager.add_ai_message(response_content)

        except Exception as e:
            logger.error(f"Agent streaming hatası: {str(e)}", exc_info=True)
            yield ERROR_MESSAGES["GENERAL_ERROR"](str(e))

    return {"run": run, "stream_run": stream_run}
