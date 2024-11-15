from transformers import pipeline
import pymongo
import gradio as gr
from huggingface_hub import InferenceClient
from model.AI_agent.LLM import LLM
from model.AI_agent.utils import convert_price_to_text
from langchain_core.messages import HumanMessage, AIMessage
import os
from model.AI_agent.NER_agent import NERAgent
from model.AI_agent.Chat_agent import ChatAgent
from model.AI_agent.Router import Router
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from typing import List

class State(TypedDict):
    chat_history: List[dict]
    user_message: str


class AIAgent:
    def __init__(self):
        self.__llm = LLM(client=InferenceClient(api_key=os.environ["HF_TOKEN"]))
        self._ner_agent = NERAgent(llm=self.__llm)
        self._chat_agent = ChatAgent(llm=self.__llm)
        self._router = Router(llm=self.__llm)

    def chat_complete(self, chat_history):
        router_path = self._router.run(chat_history)
        if router_path == "[SEARCH_HOUSE]":
            print("NER NODE")
            return self._ner_node(chat_history)
        elif router_path == "[NORMAL_CHAT]":
            print("CHAT NODE")
            return self._chat_node(chat_history)
        
    def _chat_node(self, chat_history):
        response_text = self._chat_agent.run(chat_history)
        print(response_text)
        return [response_text]
    
    def _ner_node(self, chat_history):
        user_message = chat_history[-1]['content']
        result = self._ner_agent.run(user_message)
        response = self._create_response(result)

        return response
    
    def _create_response(self, query_result):
        if len(query_result) == 0:
            return ["Xin lỗi, tôi không tìm thấy kết quả nào phù hợp với yêu cầu của bạn. Vui lòng thử lại với yêu cầu khác."]
        
        response = ["""Đây là vài kết quả mà tôi tìm được:"""]
        for i, result in enumerate(query_result):
            images = result['images']
            html_res = gr.HTML(f"""
                               <div style="display: flex; align-items: flex-start;">
                                    <div style="display: block; width: 200px; height: 200px; border: 1px solid black; overflow: hidden;">
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 3px; width: 200px; height: 200px;">
                                            <img src="{images[0]}" style="grid-column: 1 / span 2; grid-row: 1; width: 100%; height: 100px; object-fit: cover; margin: 0;" />
                                            <img src="{images[1]}" style="grid-column: 1; grid-row: 2; width: 100%; height: 100px; object-fit: cover; margin: 0;" />
                                            <img src="{images[2]}" style="grid-column: 2; grid-row: 2; width: 100%; height: 100px; object-fit: cover; margin: 0;" />
                                        </div>
                                    </div>
                                    <p style="margin-left: 10px; max-width: 400px; overflow-wrap: break-word;">
                                    {result['address']} <br>
                                    <strong>Giá:</strong> {convert_price_to_text(result['price'])} <br>
                                    <a href="{result['url']}" target="_blank" style="margin-top: 10px; display: inline-block; width: auto; border: 0">
                                        <button class="cta-button">Xem chi tiết</button>
                                    </a>
                                    </p>
                                </div>
                                """)
            response.append(html_res)
        return response

if __name__ == "__main__":
    agent = AIAgent()
    results = agent._query([{'district': 'Quận 1'}, {'min_price': 1000000000}])
    print(results)
    print(len(results))