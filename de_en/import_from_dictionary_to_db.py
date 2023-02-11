import django
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'translate.settings')
django.setup()

file_name='de_en/de-en.txt.gz'

from de_en.dictionary import GermanToEnglishDictionary
from de_en.models import GermanToEnglishDefinition
from django.db import transaction

# Read the dictionary.
print('Reading file {}...'.format(file_name))
dictionary = GermanToEnglishDictionary()
dictionary.read_from_ding_file(file_name=file_name)

dictionary_word_total_count = len(dictionary)
dictionary_word_saved_count = 0

print("Processing {} words...".format(dictionary_word_total_count))

# Replace the current database with the new words.
with transaction.atomic():

    # Clear existing database.
    GermanToEnglishDefinition.objects.all().delete()

    definitions = [GermanToEnglishDefinition(
            word=definition['word'],
            form=definition['form'],
            definition=definition['definition'],
            base_word_length=definition['base_word_length'],
            search_key=GermanToEnglishDefinition.get_search_key_for(
            definition['word'])) for definition in dictionary]

    GermanToEnglishDefinition.objects.bulk_create(definitions)

print()
