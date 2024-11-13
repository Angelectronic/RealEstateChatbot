import scrapy
from scrapy.loader import ItemLoader
from ..items import RealEstateItem, BrokersItem
import pymongo
from ..settings import MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION

class BatdongsanSpider(scrapy.Spider):
    name = "batdongsan"
    allowed_domains = ["batdongsan.com.vn"]

    START = 1
    END = 9365

    headers = {
        'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*',
        'Sec-Fetch-Mode': 'no-cors',
    }
    already_scraped_urls = []

    def __init__(self, name=None, **kwargs):
        client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        collection = client[MONGODB_DB][MONGODB_COLLECTION]
        for item in collection.find():
            self.already_scraped_urls.append(item['url'])

        super().__init__(name, **kwargs)
        
    
    def start_requests(self):
        urls = [f'https://batdongsan.com.vn/nha-dat-ban/p{self.START}']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        print(f"Scraping page {self.START}")
        real_estates = response.xpath("//a[@class='js__product-link-for-product-id' and not(@target='_blank')]")
        for real_estate in real_estates:
            url = real_estate.xpath("./@href").extract_first()
            url = 'https://batdongsan.com.vn' + url

            if url in self.already_scraped_urls:
                print(f"Already scraped {url}")
                continue
            self.already_scraped_urls.append(url)
            yield scrapy.Request(url=url, callback=self.parse_summary, headers=self.headers)
            # break

        if self.START < self.END:
            self.START += 1
            next_page = f'https://batdongsan.com.vn/nha-dat-ban/p{self.START}'
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_summary(self, response):
        if response.status == 403:
            print("Forbidden")
            return
        loader = ItemLoader(item=RealEstateItem(), selector=response)
        broker_loader = ItemLoader(item=BrokersItem(), selector=response)

        loader.add_xpath('post_id', "//div[@class='re__pr-short-info-item js__pr-config-item' and span[text()='Mã tin']]/span[@class='value']/text()")
        loader.add_xpath('title', "//h1[@class='re__pr-title pr-title js__pr-title']//text()")
        loader.add_xpath('images', "//div[@class='re__product-album']/div/@href")
        loader.add_value('url', response.url)
        loader.add_xpath('acreage', "//div[@class='re__pr-short-info-item js__pr-short-info-item' and span[text()='Diện tích']]/span[@class='value']/text()")

        price = response.xpath("//div[@class='re__pr-short-info-item js__pr-short-info-item' and span[text()='Mức giá']]/span[@class='value']/text()").extract_first()
        if "/" in price:
            price = response.xpath("//div[@class='re__pr-short-info-item js__pr-short-info-item' and span[text()='Mức giá']]/span[@class='ext']/text()").extract_first()
            price = price.replace('~', '')

        loader.add_value('price', price)
        loader.add_xpath('district', "//div[@class='re__breadcrumb js__breadcrumb js__ob-breadcrumb']/a[@level='3']/text()")
        loader.add_xpath('city', "//div[@class='re__breadcrumb js__breadcrumb js__ob-breadcrumb']/a[@level='2']/text()")
        loader.add_xpath('area', "//div[@class='re__breadcrumb js__breadcrumb js__ob-breadcrumb']/a[@level='4']/text()")
        loader.add_xpath('address', "//span[@class='re__pr-short-description js__pr-address']/text()")
        loader.add_xpath('type_of_land', "//div[@class='re__breadcrumb js__breadcrumb js__ob-breadcrumb']/a[@level='4']/text()")
        loader.add_xpath('bedroom', "//div[@class='re__pr-short-info-item js__pr-short-info-item' and span[text()='Phòng ngủ']]/span[@class='value']/text()")
        loader.add_xpath('toilet', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Số toilet']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('legal', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Pháp lý']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('interior', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Nội thất']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('balcony_direction', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Hướng ban công']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('house_direction', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Hướng nhà']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('floors', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Số tầng']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('road_in', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Đường vào']]/span[@class='re__pr-specs-content-item-value']/text()")
        loader.add_xpath('frontage', "//div[@class='re__pr-specs-content-item' and span[@class='re__pr-specs-content-item-title' and text()='Mặt tiền']]/span[@class='re__pr-specs-content-item-value']/text()")

        broker_loader.add_xpath('name', "//a[@class='js__agent-contact-name']/text()")
        broker_loader.add_xpath('url', "//a[@class='js__agent-contact-name']/@href")
        loader.add_value('broker', broker_loader.load_item())

        loader.add_xpath('description', "//div[@class='re__section re__pr-description js__section js__li-description']/div[@class='re__section-body re__detail-content js__section-body js__pr-description js__tracking']//text()")
        loader.add_xpath('posted_date', "//div[@class='re__pr-short-info-item js__pr-config-item' and span[text()='Ngày đăng']]/span[@class='value']/text()")
        loader.add_xpath('expired_date', "//div[@class='re__pr-short-info-item js__pr-config-item' and span[text()='Ngày hết hạn']]/span[@class='value']/text()")

        yield loader.load_item()