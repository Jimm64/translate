from de_en import views
from django.test import TestCase
from django.urls import reverse
from de_en.dictionary import GermanToEnglishDictionary
from de_en.models import GermanToEnglishDefinition
from unittest.mock import MagicMock, patch, mock_open
import json

# Create your tests here.


class DingDefinitionTests(TestCase):
    """ Test reading definitions from a DING file. """

    def test_reading_definition_saves_all_info(self):

        word_entries = {}

        GermanToEnglishDictionary.add_words_from_ding_definition(
            'Flugzeit {f} | Flugzeiten {pl} :: flying time | flying times',
            word_entries)

        self.assertTrue('Flugzeit' in word_entries)
        self.assertEqual(word_entries['Flugzeit']['word'], 'Flugzeit')
        self.assertEqual(word_entries['Flugzeit']['form'], 'f')
        self.assertEqual(word_entries['Flugzeit']['definition'], 'flying time')

        self.assertTrue('Flugzeiten' in word_entries)
        self.assertEqual(word_entries['Flugzeiten']['word'], 'Flugzeiten')
        self.assertEqual(word_entries['Flugzeiten']['form'], 'pl')
        self.assertEqual(word_entries['Flugzeiten']['definition'], 
            'flying times')

        self.assertEqual(len(word_entries), 2)

    def test_read_method_reads_definition_with_addendum_after_word(self):

        word_entries = {}

        GermanToEnglishDictionary.add_words_from_ding_definition(
            'das A und O [ugs.] :: the nuts and bolts [coll.]',
            word_entries)

        self.assertTrue('das A und O [ugs.]' in word_entries)
        self.assertEqual(word_entries['das A und O [ugs.]']['word'],
            'das A und O [ugs.]')
        self.assertEqual(word_entries['das A und O [ugs.]']['definition'],
            'the nuts and bolts [coll.]')
        self.assertIsNone(word_entries['das A und O [ugs.]']['form'])

    def test_read_method_reads_definition_with_addendum_after_form(self):

        word_entries = {}

        GermanToEnglishDictionary.add_words_from_ding_definition(
            'Apfelbaum {m} [bot.] | Apfelbäume {pl} :: apple tree | apple trees',
            word_entries)

        self.assertTrue('Apfelbaum' in word_entries)
        self.assertEqual(word_entries['Apfelbaum']['word'], 'Apfelbaum')
        self.assertEqual(word_entries['Apfelbaum']['form'], 'm')
        self.assertEqual(word_entries['Apfelbaum']['definition'], 'apple tree')

        self.assertTrue('Apfelbäume' in word_entries)
        self.assertEqual(word_entries['Apfelbäume']['word'], 'Apfelbäume')
        self.assertEqual(word_entries['Apfelbäume']['form'], 'pl')
        self.assertEqual(word_entries['Apfelbäume']['definition'], 'apple trees')

    def test_read_method_ignores_comments(self):

        word_entries = {}
        GermanToEnglishDictionary.add_words_from_ding_definition(
            '# Version :: 1.9 2020-12-22', word_entries)


class GermanToEnglishDictionaryTests(TestCase):

    def test_dictionary_reads_definition_from_simple_ding_file(self):

        text_file_text = \
            'Flugzeit {f} | Flugzeiten {pl} :: flying time | flying times'

        dictionary = GermanToEnglishDictionary()

        with patch('builtins.open', mock_open(read_data=text_file_text)) as mock_file:

            dictionary.read_from_ding_file(file_name='de-en.txt')
            mock_file.assert_called_with('de-en.txt', 'r')

        word_entries = [word for word in dictionary.filter(key_substring="Flugzeit")]
        self.assertEqual(len(word_entries), 2)

        self.assertEqual(word_entries[0]['word'], 'Flugzeit')
        self.assertEqual(word_entries[0]['form'], 'f')
        self.assertEqual(word_entries[0]['definition'], 'flying time')

        self.assertEqual(word_entries[1]['word'], 'Flugzeiten')
        self.assertEqual(word_entries[1]['form'], 'pl')
        self.assertEqual(word_entries[1]['definition'], 'flying times')

        word_entries = [word for word in dictionary.filter(key_substring="Flugzeiten")]
        self.assertEqual(word_entries[0]['word'], 'Flugzeiten')
        self.assertEqual(word_entries[0]['form'], 'pl')
        self.assertEqual(word_entries[0]['definition'], 'flying times')

    def test_dictionary_is_iterable(self):

        text_file_text = \
            'Flugzeit {f} | Flugzeiten {pl} :: flying time | flying times'

        dictionary = GermanToEnglishDictionary()

        with patch('builtins.open', mock_open(read_data=text_file_text)) as mock_file:

            dictionary.read_from_ding_file(file_name='de-en.txt')
            mock_file.assert_called_with('de-en.txt', 'r')

        word_entries = [word for word in dictionary]
        self.assertEqual(len(word_entries), 2)

        self.assertEqual(word_entries[0]['word'], 'Flugzeit')
        self.assertEqual(word_entries[0]['form'], 'f')
        self.assertEqual(word_entries[0]['definition'], 'flying time')

        self.assertEqual(word_entries[1]['word'], 'Flugzeiten')
        self.assertEqual(word_entries[1]['form'], 'pl')
        self.assertEqual(word_entries[1]['definition'], 'flying times')


class GermanToEnglishDictionaryFileLoadTests(TestCase):

    def test_dictionary_reads_definitions_from_actual_ding_file(self):

        dictionary = GermanToEnglishDictionary()
        dictionary.read_from_ding_file(file_name='de_en/de-en.txt.gz')

        word_entries = [word for word in dictionary.filter(key_substring="Flugzeit")]
        self.assertGreaterEqual(len(word_entries), 1)


class FilterViewTests(TestCase):

    def assert_word_is_found_by_filters_when_saved(self, *, word_filters, word, 
        word_form, word_definition):
        """
        Save a given word, and test that the given filter(s)
        retrieve it.
        """

        GermanToEnglishDefinition(word=word, form=word_form, 
            definition=word_definition, search_key=
                GermanToEnglishDefinition.get_search_key_for(word)).save()

        for word_filter in word_filters:
            response = self.client.get(reverse('filter'), 
                {'filter': word_filter})
            matching_words = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(matching_words), 1)
        self.assertEqual(matching_words[0]['word'], word)
        self.assertEqual(matching_words[0]['form'], word_form)
        self.assertEqual(matching_words[0]['definition'], word_definition)

    def test_filter_request_with_no_text_gets_422_status_code(self):

        response = self.client.get(reverse('filter'))
        self.assertEqual(response.status_code, 422)

    def test_request_with_no_match_returns_empty_response(self):

        response = self.client.get(reverse('filter'), {'filter':'F'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '[]')

    def test_filter_request_with_match_returns_the_match(self):

        self.assert_word_is_found_by_filters_when_saved(
            word_filters=['Flug', 'Flugzeit'],
            word='Flugzeit', word_form='f',
            word_definition='flying time')

    def test_filter_for_word_with_unicode_char_returns_matching_word(self):

        self.assert_word_is_found_by_filters_when_saved(
            word_filters=['Frühstück'],
            word='Frühstück', word_form='n', word_definition='breakfast')

    def test_filter_for_word_without_umlaut_matches_word_with_umlaut(self):

        self.assert_word_is_found_by_filters_when_saved(
            word_filters=['Frühstuck'],
            word='Frühstück', word_form='n', word_definition='breakfast')

    def test_filter_request_with_two_matches_returns_both_matches(self):
        
        GermanToEnglishDefinition(word='Flugzeit', form='f', 
            definition='flying time',
            search_key=GermanToEnglishDefinition.get_search_key_for(
                'Flugzeit')).save()
        GermanToEnglishDefinition(word='Flugzeiten', form='pl', 
            definition='flying times',
            search_key=GermanToEnglishDefinition.get_search_key_for(
                'Flugzeiten')).save()

        response = self.client.get(reverse('filter'), {'filter':'Flug'})
        self.assertEqual(response.status_code, 200)
        matching_words = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(matching_words), 2)

        self.assertEqual(matching_words[0]['word'], 'Flugzeit')
        self.assertEqual(matching_words[0]['form'], 'f')
        self.assertEqual(matching_words[0]['definition'], 'flying time')

        self.assertEqual(matching_words[1]['word'], 'Flugzeiten')
        self.assertEqual(matching_words[1]['form'], 'pl')
        self.assertEqual(matching_words[1]['definition'], 'flying times')
    
    def test_filter_request_with_limit_1_only_returns_one_match(self):
        
        GermanToEnglishDefinition(word='Flugzeit', form='f', 
            definition='flying time',
            search_key=GermanToEnglishDefinition.get_search_key_for(
                'Flugzeit')).save()
        GermanToEnglishDefinition(word='Flugzeiten', form='pl', 
            definition='flying times',
            search_key=GermanToEnglishDefinition.get_search_key_for(
                'Flugzeiten')).save()

        response = self.client.get(reverse('filter'), {'filter':'Flug',
            'limit': 1})
        self.assertEqual(response.status_code, 200)
        matching_words = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(matching_words), 1)
        self.assertEqual(matching_words[0]['word'], 'Flugzeit')
        self.assertEqual(matching_words[0]['form'], 'f')
        self.assertEqual(matching_words[0]['definition'], 'flying time')

    def test_filter_request_gets_matches_in_length_order(self):

        GermanToEnglishDefinition(word='aaa', form='f', 
            definition='def',
            search_key=GermanToEnglishDefinition.get_search_key_for(
            'aaa')).save()
        GermanToEnglishDefinition(word='aaaa', form='f', 
            definition='def',
            search_key=GermanToEnglishDefinition.get_search_key_for(
            'aaaa')).save()
        GermanToEnglishDefinition(word='a', form='f', 
            definition='def',
            search_key=GermanToEnglishDefinition.get_search_key_for(
            'a')).save()
        GermanToEnglishDefinition(word='aa', form='f', 
            definition='def',
            search_key=GermanToEnglishDefinition.get_search_key_for(
            'aa')).save()

        response = self.client.get(reverse('filter'), {'filter':'aa'})
        self.assertEqual(response.status_code, 200)
        matching_words = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(matching_words), 3)
        self.assertEqual(matching_words[0]['word'], 'aa')
        self.assertEqual(matching_words[1]['word'], 'aaa')
        self.assertEqual(matching_words[2]['word'], 'aaaa')

    def test_filter_request_with_invalid_limit_returns_422_status_code(self):

        GermanToEnglishDefinition(word='Flugzeit', form='f', 
            definition='flying time',
            search_key=GermanToEnglishDefinition.get_search_key_for(
            'Flugzeit')).save()

        for value in [-1, views.MAX_WORD_MATCH_LIMIT + 1, 0, 'a']:

            response = self.client.get(reverse('filter'), {'filter':'Flug', 'limit': value})
            self.assertEqual(response.status_code, 422)

    def test_lookup_page_request_returns_something(self):
            response = self.client.get(reverse('lookup'))
            self.assertEqual(response.status_code, 200)
