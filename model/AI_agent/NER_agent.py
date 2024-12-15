from transformers import pipeline
import pymongo
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
import copy

class NERAgent:
    def __init__(self, llm: BaseChatModel, limit_query = 3, model_checkpoint = "model/ViT5-real-estate-ner"):
        self.__ner_pipeline = pipeline("ner", model=model_checkpoint, aggregation_strategy="simple", device=0)
        self.__collection = pymongo.MongoClient("mongodb://localhost:27017")["real_estate"]["batdongsan"]
        self.__limit_query = limit_query
        self.__llm = llm
        self. __rewrite_prompt = [
            { "role": "system", "content": "Viết lại câu sau cho mạch lạc, dễ hiểu và đúng ngữ pháp hơn. Đảm bảo câu văn có giọng điệu trang trọng và chuyên nghiệp, đồng thời loại bỏ từ viết tắt hoặc từ không cần thiết nếu có" },
            { "role": "user", "content": "Cho tôi nhà ở hà nội có hướng TaayBawc ban công, từ 1 tỷ đến 2 tỷ, diện tích từ 50 đến 100m2" },
            { "role": "assistant", "content": "Tìm nhà ở Hà Nội có ban công hướng Tây - Bắc, giá từ 1 tỷ đến 2 tỷ, diện tích từ 50 m2 đến 100 m2" },
            { "role": "user", "content": "nhà ở nam định nào có hướng đông, ban công Nam Đông, trong khoảng từ một đến hai tỷ, diện tích từ 75 đến một trăm mét vuông" },
            { "role": "assistant", "content": "Tìm nhà ở Nam Định có ban công hướng Đông, ban công hướng Đông - Nam, giá từ 1 tỷ đến 2 tỷ, diện tích từ 75 m2 đến 100 m2" },
            { "role": "user", "content": "Có nhà nào ở hà đông, hà nội với giá dưới 2 tỷ không?" },
            { "role": "assistant", "content": "Tìm nhà ở Hà Đông, Hà Nội có giá dưới 2 tỷ" }
        ]

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

    def run(self, user_message):
        message = self.__llm.invoke([HumanMessage(content=user_message)], chat_history=copy.deepcopy(self.__rewrite_prompt)).content
        print(message)

        entites = self.__ner_pipeline(message)
        format_entities = self._format_entities(entites)
        print(format_entities)
        
        result = self._query(format_entities)
        return result

        
    