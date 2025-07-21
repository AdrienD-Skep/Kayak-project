import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ctypes


class BookingSpider(scrapy.Spider):
    name = "BookingSpider1"
    start_urls = ['https://www.booking.com/']
    cities = ["Mont Saint Michel",
"St Malo"]


    def __init__(self, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in your PATH

    def parse(self, response):
        # Prevent PC from sleeping
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        for city in self.cities:
            self.log(f"Processing city: {city}", level=logging.INFO)
            self.driver.get(response.url)
            time.sleep(5)  # Wait before interacting with the search box
            
            search_box = self.driver.find_element(By.NAME, 'ss')
            search_box.clear()  # Clear any existing text in the search box
            for i in range(50):  # Send multiple backspaces to ensure the box is cleared
                search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(1)  # Small pause for clarity
            search_box.send_keys(city)
            time.sleep(2)  # Wait before hitting Enter
            search_box.send_keys(Keys.RETURN)
            
            # Wait for the page to load
            time.sleep(5)
            current_url = self.driver.current_url
            modified_url = current_url + '&nflt=ht_id%3D204'
            self.driver.get(modified_url)
            
            # Wait for the filtered results to load
            time.sleep(5)

            # Scroll and click "Afficher plus de résultats" button if present
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Adjust the sleep time to be more cautious
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    try:
                        show_more_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'a83ed08757') and contains(., 'Afficher plus de résultats')]"))
                        )
                        show_more_button.click()
                        time.sleep(3)  # Wait for more results to load
                    except:
                        break
                else:
                    last_height = new_height

            # Now pass the page source to Scrapy
            response = scrapy.http.TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
            yield from self.parse_results(response, city)
        # Allow the PC to sleep again after the process completes
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    
    def parse_results(self, response, city):
        search_results = response.xpath('//*[@id="bodyconstraint-inner"]/div/div/div[2]/div[3]/div[2]/div[2]/div[3]/div')
        for search_result in search_results:
            result_name = search_result.xpath('div[1]/div[2]/div/div/div[1]/div/div[1]/div/h3/a/div[1]/text()').get()
            if result_name:
                yield {
                    'city': city,
                    'Result name': result_name,
                    'url': search_result.xpath('div[1]/div[2]/div/div/div[1]/div/div[1]/div/h3/a').attrib["href"].split('?')[0]
                }
                

    
    def closed(self, reason):
        self.driver.quit()

filename = "BookingInfo.json"

if filename in os.listdir('src'):
    os.remove('src/' + filename)

process = CrawlerProcess(settings={
    'USER_AGENT': 'Chrome/129.0.6668.101',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename: {"format": "json"},
    }
})

process.crawl(BookingSpider)
process.start()