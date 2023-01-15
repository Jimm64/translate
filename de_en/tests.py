from django.test import TestCase
from de_en.dictionary import GermanToEnglishDictionary
from unittest.mock import MagicMock, patch, mock_open

# Create your tests here.

class DingDefinitionTests(TestCase):
    """ Test reading definitions from a DING file. """

    def test_reading_definition_saves_all_info(self):

        word_entries = {}

        GermanToEnglishDictionary.add_words_from_ding_definition(
            'Flugzeit {f} | Flugzeiten {pl} :: flying time | flying times',
            word_entries)

        self.assertTrue('Flugzeit' in word_entries)
        self.assertEqual(word_entries['Flugzeit']['form'], 'f')
        self.assertEqual(word_entries['Flugzeit']['definition'], 'flying time')

        self.assertTrue('Flugzeiten' in word_entries)
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
        self.assertEqual(word_entries['das A und O [ugs.]']['definition'],
            'the nuts and bolts [coll.]')
        self.assertIsNone(word_entries['das A und O [ugs.]']['form'])

    def test_read_method_reads_definition_with_addendum_after_form(self):

        word_entries = {}

        GermanToEnglishDictionary.add_words_from_ding_definition(
            'Apfelbaum {m} [bot.] | Apfelbäume {pl} :: apple tree | apple trees',
            word_entries)

        self.assertTrue('Apfelbaum' in word_entries)
        self.assertEqual(word_entries['Apfelbaum']['form'], 'm')
        self.assertEqual(word_entries['Apfelbaum']['definition'], 'apple tree')

        self.assertTrue('Apfelbäume' in word_entries)
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

    def test_dictionary_reads_definitions_from_actual_ding_file(self):

        dictionary = GermanToEnglishDictionary()
        dictionary.read_from_ding_file(file_name='de_en/de-en.txt.gz')

        word_entries = [word for word in dictionary.filter(key_substring="Flugzeit")]
        self.assertGreaterEqual(len(word_entries), 1)

