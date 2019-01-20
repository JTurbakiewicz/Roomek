import scrapy
#from scraping_cleaner import extract_and_clean_by_xpath
try:
    import cpickle as pickle
except:
    import pickle


with open('plik.txt', 'w') as f:
    f.write('')


class OlxSpiderSub(scrapy.Spider):
    name = "olx_spider_sub"

    def start_requests(self):
        with open('olx_scraped_urls.pickle', 'rb') as f:
            urls = pickle.load(f)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        def save_to_file(label, what_to_save):
            advert_list[label] = what_to_save

        advert_list = {}

        # some of the basic data in the OLX subpage. Generally, they are always placed in the same spot.
        basic_offer_data = {
            'offer_name': '//*[@id="offerdescription"]/div[2]/h1/text()',
            'price': '//*[@id="offeractions"]/div[1]/strong/text()',
            'offer_location': '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()',
            'date_of_the_offer': '//*[@id="offerdescription"]/div[2]/div[1]/em/text()',
            'offer_id': '//*[@id="offerdescription"]/div[2]/div[1]/em/small/text()',
            'offer_text': '//*[@id="textContent"]/text()'
        }

        for key, key_xpath in basic_offer_data.items():
            save_to_file(key, extract_and_clean_by_xpath(key_xpath))

        for column in range(1, 5):
            for row in range(1, 3):
                key = extract_and_clean_by_xpath(
                    f'//*[@id="offerdescription"]/div[3]/table/tr[{column}]/td[{row}]/table/tr/th/text()')
                value = extract_and_clean_by_xpath(
                    f'//*[@id="offerdescription"]/div[3]/table/tr[{column}]/td[{row}]/table/tr/td/strong/a/text()')
                if value is None:
                    value = extract_and_clean_by_xpath(
                        f'//*[@id="offerdescription"]/div[3]/table/tr[{column}]/td[{row}]/table/tr/td/strong/text()')
                if key is not None:
                    save_to_file(key, value)

        aggregated_offer_text = []

        for paragraph_in_offer_text in range(1,50):
            offer_text_xpath = f'//*[@id="textContent"]/text()[{paragraph_in_offer_text}]'
            offer_text_paragraph = extract_and_clean_by_xpath(offer_text_xpath)
            if offer_text_paragraph is None:
                break
            aggregated_offer_text.append(offer_text_paragraph)
        save_to_file('offer_text', ' '.join(aggregated_offer_text))

        with open('plik.txt', 'a') as f:
            f.write(str(advert_list) + '\n')
