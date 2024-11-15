from transformers import pipeline
import pymongo
from langchain_core.language_models.chat_models import BaseChatModel
import os
from langchain_core.messages import HumanMessage, AIMessage

class ChatAgent:
    def __init__(self, llm: BaseChatModel):
       self.__llm = llm

    def run(self, chat_history):
        input_llm = []
        for chat in chat_history:
            if chat['role'] == "user":
                input_llm.append(HumanMessage(content=chat['content']))
            elif chat['role'] == "assistant":
                input_llm.append(AIMessage(content=chat['content']))
        
        llm_response = self.__llm.invoke(input_llm, chat_history=[{"role": "system", "content": "Bạn là một trợ lý ảo về bất động sản."}])

        return llm_response.content