from transformers import pipeline
import pymongo
import gradio as gr
from huggingface_hub import InferenceClient
from model.AI_agent.LLM import LLM
from model.AI_agent.utils import convert_price_to_text
from langchain_core.messages import HumanMessage, AIMessage
import os

class AIAgent:
    def __init__(self, model_checkpoint = "model/ViT5-real-estate-ner", limit_query = 3):
        self.__ner_pipeline = pipeline("ner", model=model_checkpoint, aggregation_strategy="simple", device=0)
        self.__collection = pymongo.MongoClient("mongodb://localhost:27017")["real_estate"]["batdongsan"]
        self.__limit_query = limit_query
        self.__llm = LLM(client=InferenceClient(api_key=os.environ["HF_TOKEN"]))
        self.__intent_classify_prompt = [
            { "role": "system", "content": "Bạn là một trợ lý ảo. Nếu người dùng hỏi những câu liên quan đến bất động sản, tìm nhà, hãy trả lời \"[CALL_TOOL]\". Còn lại thì trả lời như bình thường" },
            { "role": "user", "content": "Xin chào" },
            { "role": "assistant", "content": "Xin chào! Rất vui được gặp bạn. Tôi có thể giúp gì cho bạn hôm nay?" },
            { "role": "user", "content": "Tìm nhà ở Hà Nội" },
            { "role": "assistant", "content": "[CALL_TOOL]" },
            { "role": "user", "content": "Bạn là ai" },
            { "role": "assistant", "content": "Xin chào! Tôi là trợ lý ảo của bạn, được tạo ra để hỗ trợ bạn trong nhiều vấn đề khác nhau. Tôi có thể giúp bạn tìm thông tin, giải đáp thắc mắc, và nhiều hơn thế. Bạn cần tôi giúp gì hôm nay?" },
            { "role": "user", "content": "Cho tôi thông tin về chung cư mini ở Hồ Chí Minh" },
            { "role": "assistant", "content": "[CALL_TOOL]" }
        ]
        self. __rewrite_prompt = [
            { "role": "system", "content": "Viết lại câu sau cho mạch lạc, dễ hiểu và đúng ngữ pháp hơn. Đảm bảo câu văn có giọng điệu trang trọng và chuyên nghiệp, đồng thời loại bỏ từ viết tắt hoặc từ không cần thiết nếu có" },
            { "role": "user", "content": "Cho tôi nhà ở hà nội có hướng TaayBawc ban công, từ 1 tỷ đến 2 tỷ, diện tích từ 50 đến 100m2" },
            { "role": "assistant", "content": "Tìm nhà ở Hà Nội có ban công hướng Tây - Bắc, giá từ 1 tỷ đến 2 tỷ, diện tích từ 50 m2 đến 100 m2" },
            { "role": "user", "content": "nhà ở nam định nào có hướng đông, ban công Nam Đông, trong khoảng từ một đến hai tỷ, diện tích từ 75 đến một trăm mét vuông" },
            { "role": "assistant", "content": "Tìm nhà ở Nam Định có ban công hướng Đông, ban công hướng Đông - Nam, giá từ 1 tỷ đến 2 tỷ, diện tích từ 75 m2 đến 100 m2" }
        ]

    def chat_complete(self, chat_history):
        input_llm = []
        for chat in chat_history:
            if chat['role'] == "user":
                input_llm.append(HumanMessage(content=chat['content']))
            elif chat['role'] == "assistant":
                input_llm.append(AIMessage(content=chat['content']))
        
        llm_response = self.__llm.invoke(input_llm, chat_history=self.__intent_classify_prompt)

        if llm_response.content == "[CALL_TOOL]":
            print("NER NODE")
            user_message = chat_history[-1]['content']
            rewrite_response = self.__llm.invoke([HumanMessage(content=user_message)], chat_history=self.__rewrite_prompt)
            print(rewrite_response.content)
            return self._ner_node(rewrite_response.content)
        else:
            print("LLM NODE")
            print(llm_response.content)
            return [llm_response.content.replace("[CALL_TOOL]", "")]
        
    def _rewrite_message(self, message):
        pass
    
    def _ner_node(self, user_message):
        entites = self.__ner_pipeline(user_message)
        format_entities = self._format_entities(entites)
        print(format_entities)
        result = self._query(format_entities)
        response = self._create_response(result)

        return response
    
    def _format_entities(self, entities):
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
    
    def _query(self, entities):
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
    

if __name__ == "__main__":
    agent = AIAgent()
    results = agent._query([{'district': 'Quận 1'}, {'min_price': 1000000000}])
    print(results)
    print(len(results))