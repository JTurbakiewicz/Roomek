#TEST BRANCZA

import Witai.witai_connection as wit
import Databases.mysql_connection as sql
import re
import logging
from time import sleep
from math import ceil
from Scraper.PropertyScraper.items import OfferItem
from Scraper.PropertyScraper.util import offer_features
import inspect
import clean_output as cn


logging.basicConfig(level='DEBUG')

class Parser():

    def __init__(self, relevant_word = 'def', sql_column_name = 'offer_text'):
        self.relevant_word = relevant_word
        self.sql_column_name = sql_column_name
        self.sql_train_data = sql.get_custom(
            """select offer_url, offer_text, {0} from offers where {0} is not Null and offer_text like '%{1}%'""".format(sql_column_name,relevant_word))
        self.train_batch_size = len(self.sql_train_data)
        self.sql_parse_data = sql.get_custom(
            """select offer_url, offer_text from offers where {0} is Null and offer_text like '%{1}%'""".format(sql_column_name,relevant_word))
        self.parse_batch_size = len(self.sql_parse_data)
        self.sql_parse_features_data = sql.get_custom("""select offer_url, offer_text from offers""")
        wit.create_new_entity(sql_column_name, entity_description = 'Created via OfferParser')
        wit.update_entity(sql_column_name, lookups = ["free-text", 'keywords'])

    def divide_chunks(self, list, size):
        for i in range(0, len(list), size):
            yield list[i:i + size]

    def prepare_input(self, data_to_prepare, values_present):
        logging.debug(data_to_prepare)
        sent_end_pattern = re.compile(r'\. ')
        capital_pattern = re.compile(r'[A-Z]')
        final_sentences = []
        final_values = []
        start_chars = []
        end_chars = []
        offer_urls = []
        for record in data_to_prepare:
            url = record['offer_url']
            if values_present:
                value = record[self.sql_column_name]
            else:
                value = 'Value not available'

            record = record['offer_text']
            sentences = re.split(sent_end_pattern, record)
            sentence_missing = True
            for sentence in sentences:
                if (self.relevant_word.lower() in sentence.lower()) and sentence_missing:
                    sentence_index = sentences.index(sentence)
                    try:
                        sentence = sentence + ' ' + sentences[sentence_index+1]
                    except:
                        pass


                    word_position = sentence.lower().find(self.relevant_word.lower())
                    sentence_end = re.split(capital_pattern, sentence[word_position + 1:])[0]
                    new_sentence = sentence[:word_position + 1] + sentence_end

                    rest_of_the_sentence = sentence[len(new_sentence):]
                    rest_of_the_sentence_split = rest_of_the_sentence.split(' ')
                    for part in rest_of_the_sentence_split:
                        try:
                            if part[0].isupper():
                                new_sentence = new_sentence + part + ' '
                            else:
                                break
                        except:
                            break

                    sentence = new_sentence

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

    def parse_wit(self, confidence_req = 0.9, output_processing_funtion = None):
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
                        if output_processing_funtion:
                            value = output_processing_funtion(value)
                        logging.info('Parsed sentence: ' + sentence)
                        logging.info('Updated offer: ' + offer_url + ' column: ' + self.sql_column_name + ' with: ' + str(value))
                        sql.update_field(table_name='offers', field_name=self.sql_column_name, field_value=value,
                                         where_field='offer_url', where_value=offer_url, if_null_required=True)
                    except Exception as e:
                        print('Error is ', e)

    def parse_simple(self):
        print(len(self.sql_parse_features_data))
        results = {
            'records_to_parse': len(self.sql_parse_features_data),
            'amount_of_updated_sentences' : 0,
            'amount_of_updated_values': 0,
        }
        sent_end_pattern = re.compile(r'\. ')
        for record in self.sql_parse_features_data:
            sentence_updated = False
            url = record['offer_url']
            record = record['offer_text']
            if record is None: continue
            sentences = re.split(sent_end_pattern, record)
            for sentence in sentences:
                for key in offer_features.keys():
                    if key.upper() in sentence.upper():
                        if not sentence_updated:
                            sentence_updated = True
                            results['amount_of_updated_sentences'] = results['amount_of_updated_sentences'] + 1
                        results['amount_of_updated_values'] = results['amount_of_updated_values'] + 1
                        logging.info('Parsed sentence: ' + sentence)
                        logging.info('Updated offer: ' + url + ' column: ' + offer_features[key] + ' with: ' + 'True')
                        try:
                            sql.update_field(table_name='offer_features', field_name=offer_features[key], field_value=1,
                                             where_field='offer_url', where_value=url, if_null_required=True)
                        except Exception as e:
                            logging.debug(e)


        return results

    def train(self, train_percent):
        self.train_percent = train_percent
        self.train_sentences, self.train_values, self.start_chars, self.end_chars, *rest = self.prepare_input(self.sql_train_data, values_present=True)
        sentences_to_train= list(self.divide_chunks(self.train_sentences[:int(self.train_batch_size*self.train_percent/100)], 200))
        values_to_train = list(self.divide_chunks(self.train_values[:int(self.train_batch_size*self.train_percent/100)], 200))
        start_chars_to_train = list(
            self.divide_chunks(self.start_chars[:int(self.train_batch_size * self.train_percent / 100)], 200))
        end_chars_to_train = list(
            self.divide_chunks(self.end_chars[:int(self.train_batch_size * self.train_percent / 100)], 200))

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
        logging.info('Verify sample size is: ' + str(results['verify_sample_size']) + '. The check will take around: ' + str(results['verify_sample_size']) + ' s.')
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

        return results

def batch_parse(min_accuracy):

    simple_parse = Parser()
    simple_parsing_results = simple_parse.parse_simple()
    logging.info(simple_parsing_results)

    fields_to_parse_wit = {
        'security_deposit' : {'relevant_word':['kaucj'], 'confidence_req' : 0.9, 'output_processing_funtion': cn.to_int},
        'street': {'relevant_word': ['ul'], 'confidence_req': 0.9, 'output_processing_funtion': cn.to_nominative}
    }

    for sql_field, parse_data in fields_to_parse_wit.items():
        for relevant_word in parse_data['relevant_word']:
            logging.info('Creating parser for: ' + str(sql_field) + '; keyword: ' + relevant_word)
            parser = Parser(relevant_word, sql_field)
            logging.info('Training parser for: ' + str(sql_field) + ' keyword: ' + relevant_word)
            parser.train(80)
            logging.info('Verifing parser for: ' + str(sql_field) + '; keyword: ' + relevant_word)
            res = parser.verify(20)
            try:
                entity_correct = res['correct_entity'] / (res['correct_entity']+res['wrong_entity'])
                value_correct = res['correct_value'] / (res['correct_value'] + res['wrong_value'])
            except ZeroDivisionError:
                logging.info('Sample size is 0, check is stopped')
                entity_correct = 0
                value_correct = 0
            logging.info('Entity check is correct in: ' + str(entity_correct))
            logging.info('Value check is correct in: ' + str(value_correct))
            if entity_correct > min_accuracy and value_correct > min_accuracy:
                logging.info('Checks approved. Starting parsing for: ' +  str(sql_field) + ' key word: ' + relevant_word)
                parser.parse_wit(output_processing_funtion=parse_data['output_processing_funtion'], confidence_req=parse_data['confidence_req'])
            else:
                logging.info('Checks disapproved. Closing parsing for: ' + str(sql_field) + ' key word: ' + relevant_word)


batch_parse(0.5)