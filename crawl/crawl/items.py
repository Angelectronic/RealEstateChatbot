# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
import datetime

def convert_price_to_number(price):
    num_path = price.split(' ')[0]
    num_path = num_path.replace('.', '')
    num_path = num_path.replace(',', '.')
    text_path = price.split(' ')[1]
    if text_path == 'tỷ':
        price = float(num_path) * 1000000000
    elif text_path == 'triệu':
        price = float(num_path) * 1000000
    return price

def extract_area(text):
    area = text.split(' tại ')[1]
    return area

def extract_type_of_land(text):
    type_of_land = text.split(' tại ')[0]
    return type_of_land

def convert_bedroom_to_number(bedroom):
    try:
        bedroom = bedroom.split(' ')[0]
        bedroom = int(bedroom)
    except:
        pass
    return bedroom

def convert_acreage_to_number(acreage):
    try:
        acreage = acreage.split(' ')[0]
        acreage = acreage.replace('.', '')
        acreage = acreage.replace(',', '.')
        acreage = float(acreage)
    except:
        pass
    return acreage

def convert_date(date):
    try:
        date = datetime.datetime.strptime(date, '%d/%m/%Y')
    except:
        pass
    return date

class BrokersItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    url = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))

class RealEstateItem(scrapy.Item):
    post_id = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    title = scrapy.Field(output_processor=' '.join, input_processor=MapCompose(str.strip))
    images = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    acreage = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_acreage_to_number))
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_price_to_number))
    district = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    city = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    area = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, extract_area))
    address = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    type_of_land = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, extract_type_of_land))
    bedroom = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_bedroom_to_number))
    toilet = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_bedroom_to_number))
    legal = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    interior = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    balcony_direction = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    house_direction = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    floors = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_bedroom_to_number))
    road_in = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_acreage_to_number))
    frontage = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_acreage_to_number))
    broker = scrapy.Field(serializer=BrokersItem, output_processor=TakeFirst())
    description = scrapy.Field(input_processor=MapCompose(str.strip), output_processor='/n'.join)
    posted_date = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_date))
    expired_date = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip, convert_date))
    