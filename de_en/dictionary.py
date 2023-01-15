import gzip
import magic
import re

class GermanToEnglishDictionary:
    """
    Loads a german-to-english dictionary from Ding's dictionary file
    (https://www-user.tu-chemnitz.de/~fri/ding/).
    """

    def __init__(self):
        self._german_words = {}

    def add_words_from_ding_definition(definition_text, word_dictionary):
        """ Add word definitions from a line in DING's text file. """

        # Example line: 
        #'Flugzeit {f} | Flugzeiten {pl} :: flying time | flying times'

        # Ignore comment lines.
        if re.match('\s*#', definition_text):
            return 

        # Divide line up into a list of words and a list of definitions.
        # Strip any whitespace.
        words, definitions = definition_text.split("::")
        words = [word.strip() for word in words.split('|')]
        definitions = [definition.strip() for definition in 
            definitions.split('|')]

        if len(words) != len(definitions):
            raise ValueError('Unequal number of words and definitions in line'
                    'for words: {}'.format(words))

        for i in range(len(words)):

            word_parameters = re.match(

                # Get everyting up to a '{'
                # Word entries may include space, punctuation, or addemdums.
                '([^{]+)' 

                # If there's a form, e.g. '{pl}' present, get it.
                '(?:{([^}]+)})?', 

                words[i])

            if not word_parameters:
                raise ValueError('Unable to parse line with words: {}'.format(
                    words[i]))

            word_parameters = word_parameters.groups()
            word_key = word_parameters[0].strip()
            word_entry = {
                'word': word_key,
                'definition': definitions[i]
            }

            if word_parameters[1]:
                word_entry['form'] = word_parameters[1]
            else:
                word_entry['form'] = None

            word_dictionary[word_key] = word_entry

    def read_from_ding_file(self, *, file_name):
        """
        Read definitions from a dictionary in Ding's format.
        File may be a Gzip file or plain text.
        """

        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            if m.id_filename(file_name) == 'application/gzip':
                dictionary_text = gzip.open(file_name, 'rt')
            else:
                dictionary_text = open(file_name, 'r')

        for definition_text in dictionary_text:
            GermanToEnglishDictionary.add_words_from_ding_definition(
            definition_text, self._german_words)

    def __iter__(self):
        """ Get an iterable of all words in the dictionary. """

        def _word_generator(self):
            for key in self._german_words:
                yield self._german_words[key]
        return _word_generator(self)

    def __len__(self):
        """ Get the number of words in the dictionary. """
        return len(self._german_words)

    def filter(self, *, key_substring):
        """ Get an iterable filter matching the given substring. """

        for key in self._german_words:
            if key_substring in key:
                yield self._german_words[key]
