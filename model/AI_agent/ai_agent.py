from transformers import pipeline
import pymongo
import gradio as gr
from huggingface_hub import InferenceClient
from model.AI_agent.LLM import LLM
from model.AI_agent.utils import convert_price_to_text
from langchain_core.messages import HumanMessage, AIMessage

class AIAgent:
    def __init__(self, model_checkpoint = "model/ViT5-real-estate-ner", limit_query = 3):
        self.__ner_pipeline = pipeline("ner", model=model_checkpoint, aggregation_strategy="simple", device=0)
        self.__collection = pymongo.MongoClient("mongodb://localhost:27017")["real_estate"]["batdongsan"]
        self.__limit_query = limit_query
        self.__llm = LLM(client=InferenceClient(api_key="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"))

    def chat_complete(self, chat_history):
        input_llm = []
        for chat in chat_history:
            if chat['role'] == "user":
                input_llm.append(HumanMessage(content=chat['content']))
            elif chat['role'] == "assistant":
                input_llm.append(AIMessage(content=chat['content']))
        
        llm_response = self.__llm.invoke(input_llm)

        if llm_response.content == "[CALL_TOOL]":
            print("NER NODE")
            user_message = chat_history[-1]['content']
            return self.__ner_node(user_message)
        else:
            print("LLM NODE")
            print(llm_response.content)
            return [llm_response.content.replace("[CALL_TOOL]", "")]
    
    def __ner_node(self, user_message):
        entites = self.__ner_pipeline(user_message)
        format_entities = self.__format_entities(entites)
        print(format_entities)
        result = self.__query(format_entities)
        response = self.__create_response(result)

        return response
    
    def __format_entities(self, entities):
        # format_entities = []
        # for e in entities:
        #     exist_keys = [list(entity.keys())[0] for entity in format_entities]
        #     if e['entity_group'] not in exist_keys:
        #         format_entities.append({f"{e['entity_group']}": e['word'].strip()})
        #     else:
        #         for entity in format_entities:
        #             if list(entity.keys())[0] == e['entity_group']:
        #                 entity[e['entity_group']] += f"{e['word'].strip()}"

        return [{f"{entity['entity_group']}": entity['word']} for entity in entities]
    
    def __create_response(self, query_result):
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
    
    def __query(self, entities):
        type_1 = ['house_direction', 'balcony_direction', 'district', 'type_of_land', 'city', 'legal']
        type_2 = ['min_price', 'max_price', 'max_acreage', 'min_acreage']

        query = {}
        for entity in entities:
            for key, value in entity.items():
                if key in type_1:
                    query[key] = {"$regex": value, "$options": "i"}
                elif key in type_2:
                    group_name = key.split("_")[1]
                    min_max = key.split("_")[0]

                    if group_name == "price":
                        value = value.replace(",", ".").strip()
                        unit = value.find("tỷ")
                        if unit != -1:
                            number = value.replace("tỷ", "").strip()
                            value = float(number) * 1000000000
                        else:
                            unit = value.find("triệu")
                            number = value.replace("triệu", "").strip()
                            value = float(number) * 1000000

                    elif group_name == "acreage":
                        number = value.replace("m2", "").strip()
                        value = float(number)

                    if min_max == "min":
                        query[group_name] = {"$gte": value}
                    else:
                        query[group_name] = {"$lte": value}
        print(query)
        result = self.__collection.find(query).limit(self.__limit_query)
        return list(result)
    
    def test_query(self, entities):
        return self.__query(entities)
    

if __name__ == "__main__":
    agent = AIAgent()
    results = agent.test_query([{'district': 'Quận 1'}, {'min_price': 1000000000}])
    print(results)
    print(len(results))