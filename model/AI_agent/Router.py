from transformers import pipeline
import pymongo
from langchain_core.language_models.chat_models import BaseChatModel
import os
from langchain_core.messages import HumanMessage, AIMessage

class Router:
    def __init__(self, llm: BaseChatModel):
       self.__llm = llm
       self.__intent_classify_prompt = [
            { "role": "system", "content": "Bạn là một trợ lý ảo chuyên phân loại ý định dựa trên câu chat của người dùng (intent classification). Nếu người dùng muốn tìm nhà, hãy trả lời \"[SEARCH_HOUSE]\". Còn lại thì trả lời \"[NORMAL_CHAT]\"" },
            { "role": "user", "content": "Xin chào" },
            { "role": "assistant", "content": "Xin chào! Rất vui được gặp bạn. Tôi có thể giúp gì cho bạn hôm nay?" },
            { "role": "user", "content": "Tìm nhà ở Hà Nội" },
            { "role": "assistant", "content": "[SEARCH_HOUSE]" },
            { "role": "user", "content": "Bạn là ai" },
            { "role": "assistant", "content": "[NORMAL_CHAT]" },
            { "role": "user", "content": "Cho tôi thông tin về chung cư mini ở Hồ Chí Minh" },
            { "role": "assistant", "content": "[SEARCH_HOUSE]" }
        ]


    def run(self, chat_history):
        user_message = chat_history[-1]['content']
        input_llm = [HumanMessage(content=user_message)]
        llm_response = self.__llm.invoke(input_llm, chat_history=self.__intent_classify_prompt)

        return llm_response.content