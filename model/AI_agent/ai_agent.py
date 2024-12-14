from transformers import pipeline
import gradio as gr
from huggingface_hub import InferenceClient
from model.AI_agent.LLM import LLM
from model.AI_agent.utils import convert_price_to_text
import os
from model.AI_agent.NER_agent import NERAgent
from model.AI_agent.Chat_agent import ChatAgent
from model.AI_agent.Router import Router
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import List, Union


class State(TypedDict):
    chat_history: List[dict]
    response_list: List[Union[str, gr.HTML]]

class AIAgent:
    def __init__(self):
        self.__llm = LLM(client=InferenceClient(api_key=os.environ["HF_TOKEN"]))
        self._ner_agent = NERAgent(llm=self.__llm)
        self._chat_agent = ChatAgent(llm=self.__llm)
        self._router = Router(llm=self.__llm)

        self._graph_builder = StateGraph(State)
        self._graph_builder.add_node("chat", self._chat_node)
        self._graph_builder.add_node("ner", self._ner_node)
        self._graph_builder.add_conditional_edges(START, self._router_node, {"chat": "chat", "ner": "ner"})
        self._graph_builder.add_edge("chat", END)
        self._graph_builder.add_edge("ner", END)
        self.app = self._graph_builder.compile()
        

    def _router_node(self, state):
        router_path = self._router.run(state['chat_history'])
        print(router_path)
        if "[NORMAL_CHAT]" in router_path:
            return "chat"
        elif "[SEARCH_HOUSE]" in router_path:
            return "ner"
        else:
            return "chat"
    
    def _chat_node(self, state):
        response_text = self._chat_agent.run(state['chat_history'])
        print(response_text)
        return {"response_list": [response_text]}
    
    def _ner_node(self, state):
        user_message = state['chat_history'][-1]['content']
        result = self._ner_agent.run(user_message)
        response = self._create_response(result)
        return {"response_list": response}

    def chat_complete(self, chat_history):
        state = self.app.invoke({"chat_history": chat_history})
        return state['response_list']
    
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