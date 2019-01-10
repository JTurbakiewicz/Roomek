import scrapy
try:
    import cpickle as pickle
except:
    import pickle

class OlxSpiderMain(scrapy.Spider):
    name = "olx_spider_main"

    def start_requests(self):
        with open('urls_to_scrape.pickle', 'rb') as f:
            urls = pickle.load(f)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        link = response.xpath('//*[@id="offers_table"]/tbody/tr/td/div/table/tbody/tr/td/div/h3/a/@href').extract()
        with open('olx_scraped_urls.pickle', 'wb') as f:
            pickle.dump(link, f)