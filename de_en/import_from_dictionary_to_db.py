import django
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'translate.settings')
django.setup()

from de_en.dictionary import GermanToEnglishDictionary
from de_en.models import GermanToEnglishDefinition
from django.db import transaction

# Read the dictionary.
dictionary = GermanToEnglishDictionary()
dictionary.read_from_ding_file(file_name='de_en/de-en.txt.gz')

dictionary_word_total_count = len(dictionary)
dictionary_word_saved_count = 0

print("Processing {} words...".format(dictionary_word_total_count))

# Replace the current database with the new words.
with transaction.atomic():

    # Clear existing database.
    GermanToEnglishDefinition.objects.all().delete()

    for definition in dictionary:
        GermanToEnglishDefinition(
            word=definition['word'],
            form=definition['form'],
            definition=definition['definition'],
            search_key=GermanToEnglishDefinition.get_search_key_for(
            definition['word'])).save()

        dictionary_word_saved_count += 1

        # Periodically report progress.
        if dictionary_word_saved_count % (dictionary_word_total_count // 100) \
            == 0:
            sys.stdout.write("\r{}% complete.".format(dictionary_word_saved_count \
                // (dictionary_word_total_count // 100)))

print()
