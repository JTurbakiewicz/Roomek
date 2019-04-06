import Witai.witai_connection as wit
import PropertyScraper.PropertyScraper.PropertyScraper_mysql_connection as sql
import re
import logging
from time import sleep
from math import ceil
from PropertyScraper.PropertyScraper.items import OfferItem
import inspect

logging.basicConfig(level='ERROR')

class Parser():

    def __init__(self, relevant_word, sql_column_name):
        self.relevant_word = relevant_word
        self.sql_column_name = sql_column_name
        self.sql_train_data = sql.get_custom(
            """select offer_url, offer_text, {0} from offers where {0} is not Null and offer_text like '%{1}%'""".format(sql_column_name,relevant_word))
        self.train_batch_size = len(self.sql_train_data)
        self.sql_parse_data = sql.get_custom(
            """select offer_url, offer_text from offers where {0} is Null and offer_text like '%{1}%'""".format(sql_column_name,relevant_word))
        self.parse_batch_size = len(self.sql_parse_data)
        wit.create_new_entity(sql_column_name, entity_description = 'Created via OfferParser')
        wit.update_entity(sql_column_name, lookups = ["free-text", 'keywords'])

    def divide_chunks(list, size):
        for i in range(0, len(list), size):
            yield list[i:i + size]

    def clean_input(self, input, type):
        if type.upper() == 'INT':
            only_numbers = re.sub(r'[^0123456789,.]', '', input)
            if '.' in only_numbers or ',' in only_numbers:
                only_numbers = only_numbers.split('.')
                if len(only_numbers[-1]) == 2:
                    only_numbers = ''.join(only_numbers[:-1])
                only_numbers = only_numbers.split(',')
                if len(only_numbers[-1]) == 2:
                    only_numbers = ''.join(only_numbers[:-1])

            return only_numbers

    def prepare_input(self, data_to_prepare, values_present):
        sent_end_pattern = re.compile(r'\. ')
        capital_pattern = re.compile(r'[A-Z]')
        final_sentences = []
        final_values = []
        start_chars = []
        end_chars = []
        offer_urls = []
        for record in data_to_prepare:
            if values_present:
                value = record[self.sql_column_name]
            else:
                value = 'Value not available'
                url = record['offer_url']
            record = record['offer_text']
            sentences = re.split(sent_end_pattern, record)
            sentence_missing = True
            for sentence in sentences:
                if (self.relevant_word.lower() in sentence.lower()) and sentence_missing:
                    word_position = sentence.lower().find(self.relevant_word.lower())
                    sentence_end = re.split(capital_pattern, sentence[word_position + 1:])[0]
                    sentence = sentence[:word_position + 1] + sentence_end
                    word_position = sentence.lower().find(self.relevant_word.lower())
                    string_to_word_position = sentence[:word_position]
                    capital_letter_positions = capital_pattern.finditer(string_to_word_position)
                    try:
                        sentence_start = list(capital_letter_positions)[-1].start()
                    except:
                        sentence_start = 0
                    complete_sentence = string_to_word_position[sentence_start:] + sentence[word_position:]
                    if str(value) in complete_sentence or not values_present:
                        final_sentences.append(complete_sentence)
                        offer_urls.append(url)
                        if values_present:
                            final_values.append(value)
                            start_chars.append((complete_sentence.find(str(value))))
                            end_chars.append((complete_sentence.find(str(value)) + len(str(value))))
                    sentence_missing = False
            if sentence_missing:
                final_sentences.append('Sentence with keyword not found')
        self.train_batch_size = len(final_sentences)

        return final_sentences, final_values, start_chars, end_chars, offer_urls

    def parse(self, expected_input_type = None, confidence_req = 0.9):
        self.parse_sentences, *rest = self.prepare_input(data_to_prepare=self.sql_parse_data, values_present=False)
        self.offer_urls = rest[-1]

        for sentence in self.parse_sentences:
            response = wit.send_message(sentence)
            try:
                response_json = response.json()
            except Exception as e:
                logging.debug(e)
            try:
                confidence = response_json['entities'][self.sql_column_name][0]['confidence']
            except KeyError:
                confidence = 0
            if confidence > confidence_req:
                try:
                    response_entity = list(response_json['entities'].keys())[0]
                except:
                    response_entity = list(response_json['entities'].keys())
                all_mysql_fields =[]
                for field in inspect.getmembers(OfferItem): all_mysql_fields.append(field[0])
                if response_entity in all_mysql_fields:
                    value = response_json['entities'][self.sql_column_name][0]['value']
                    offer_url = self.offer_urls[self.parse_sentences.index(sentence)]
                    try:
                        if expected_input_type:
                            value = self.clean_input(value, expected_input_type)
                        print(value, offer_url)
                        sql.update_field(table_name='offers', field_name=self.sql_column_name, field_value=value,
                                         where_field='offer_url', where_value=offer_url, if_null_required=True)
                    except Exception  as e:
                        print('Error is ', e)

    def train(self, train_percent):
        self.train_percent = train_percent
        self.train_sentences, self.train_values, self.start_chars, self.end_chars = self.prepare_input(self.sql_train_data, values_present=True)

        sentences_to_train= list(divide_chunks(self.train_sentences[:int(self.train_batch_size*self.train_percent/100)], 200))
        values_to_train = list(divide_chunks(self.train_values[:int(self.train_batch_size*self.train_percent/100)], 200))
        start_chars_to_train = list(
            divide_chunks(self.start_chars[:int(self.train_batch_size * self.train_percent / 100)], 200))
        end_chars_to_train = list(
            divide_chunks(self.end_chars[:int(self.train_batch_size * self.train_percent / 100)], 200))
        for batch in range(len(sentences_to_train)):
            wit.train(sentences_to_train[batch], self.sql_column_name, values_to_train[batch], start_chars=start_chars_to_train[batch], end_chars=end_chars_to_train[batch])
            if batch == len(sentences_to_train) -1:
                break
            sleep(70)
        return

    def verify(self, verify_percent):
        self.verify_percent = verify_percent
        self.train_sentences, self.train_values, *rest = self.prepare_input(data_to_prepare=self.sql_train_data, values_present=True)
        results = {
            'verify_sample_size': ceil(self.train_batch_size*self.verify_percent/100),
            'correct_entity' : 0,
            'wrong_entity': 0,
            'correct_value': 0,
            'wrong_value': 0
        }
        for sentence in self.train_sentences[int(self.train_batch_size*(100-self.verify_percent)/100):]:
            response = wit.send_message(sentence)
            response_json = response.json()
            try:
                confidence = response_json['entities'][self.sql_column_name][0]['confidence']
            except KeyError:
                confidence = 0
            if confidence > 0.9:
                try:
                    response_entity = list(response_json['entities'].keys())[0]
                except:
                    response_entity = list(response_json['entities'].keys())
                value = response_json['entities'][self.sql_column_name][0]['value']
                if response_entity == self.sql_column_name:
                    results['correct_entity'] += 1
                    sentence_index = self.train_sentences[int(self.train_batch_size*(100-self.verify_percent)/100):].index(sentence)
                    if value == str(self.train_values[int(self.train_batch_size*(100-self.verify_percent)/100):][sentence_index]):
                        results['correct_value'] += 1
                    else:
                        results['wrong_value'] += 1
                else:
                    results['wrong_entity'] += 1

        print(results)

