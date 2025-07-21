import scrapy
import logging
import os

class HotelSpider(scrapy.Spider):
    name = "hotels"
    
    # Reading URLs from a file
    with open('Hotel_url_list_test.txt', 'r') as file:
        start_urls = [line.strip() for line in file.readlines()]
    
    def __init__(self, *args, **kwargs):
        super(HotelSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        hotel_name = response.xpath('//*[@id="hp_hotel_name"]/div/h2/text()').get() 
        url = response.url

        lat, lon = response.xpath('//*[@id="map_trigger_header_pin"]/@data-atlas-latlng').get().split(',', 1)


        logging.info(f'Scraping {hotel_name} at {url}')
        address = response.xpath('//*[@id="wrap-hotelpage-top"]/div[3]/div/div/div/span[1]/button/div/text()').get()
        users_global_rating = response.xpath('//*[@id="js--hp-gallery-scorecard"]/a/div/div/div/div[1]/text()').get()
        hotel_desc = " \n ".join(response.xpath('//*[@id="basiclayout"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/p/text()').getall())
        key_features = [key_feature_name for key_feature in response.xpath('//*[@id="basiclayout"]/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div/ul/li') if (key_feature_name := key_feature.xpath('div/div/div/span/div/span/text()').get()) is not None]
        users_category_rating = {category_name: category.xpath('div/div/div[1]/div[2]/div/text()').get() for category in response.xpath('//*[@id="basiclayout"]/div[1]/div[7]/div/div[2]/div/div[4]/div/div[2]/div') if (category_name := category.xpath('div/div/div[1]/div[1]/div/span/text()').get()) is not None}
        stars = len(response.xpath('//*[@id="hp_hotel_name"]/span/div/div/span[1]/button/span/span'))
        #reviews = [review.xpath('div/div[1]/div/div/span[2]/text()').get() for review in response.xpath('/html/body/div[4]/div/div[4]/div[1]/div[1]/div[1]/div[1]/div[4]/div/div[1]/div[1]/div/div[4]/div/div[2]/ul/li')]
        # amenities = {
        #     amenity_category.xpath('div/h3/div/div/text()').get(): (
        #         [amenity_category.xpath('div/div/h3/div[2]/text()').get()] if amenity_category.xpath('div/div/h3/div[2]/text()').get() is not None else []
        #     ) + [
        #         amenity_name for amenity in amenity_category.xpath('div/ul/li') if (amenity_name := amenity.xpath('div/div/div/span/div/span/text()').get()) is not None
        #     ]
        #     for amenity_category in response.xpath('//*[@id="hp_facilities_box"]/div/div[2]/div[2]/div')
        #     if amenity_category.xpath('div/h3/div/div/text()').get() is not None
        # }
        # print(response.xpath('//*[@id="hp_facilities_box"]/div/div[2]/div[2]/div[1]').extract()) # javascript ?
        yield {
            'hotel_name': hotel_name,
            'url': url,
            'lat' : lat,
            'lon' : lon,
            'address': address,
            'users_global_rating': users_global_rating,
            'hotel_desc': hotel_desc,
            'key_features': key_features,
            'users_category_rating': users_category_rating,
            'stars' : stars,
          # 'amenities': amenities
        }

# Name of the file where the results will be saved
filename = "hotel_data.json"

# If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
if filename in os.listdir('results/'):
    os.remove('results/' + filename)
