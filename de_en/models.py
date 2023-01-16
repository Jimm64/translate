from django.db import models

# Create your models here.


class GermanToEnglishDefinition(models.Model):

    # The actual word.
    word = models.CharField(max_length=64) 

    # The form of the word e.g. m/f/n/pl
    # (as in male, female, neutral, plural)
    form = models.CharField(max_length=32,null=True)

    # The word's definition.
    definition = models.CharField(max_length=256)

    # A search key for the word. 
    search_key = models.CharField(max_length=64) 

    def get_search_key_for(word):
        """
        Return the search key to use when searching
        for the given word.

        Allows searching for words with german-specific letters by using
        similar english ones, e.g.  'a' matches 'ä', 'ss' matches 'ß' (and vice
        versa).
        """

        character_translation = {
            'Ä': 'A',
            'ä': 'a',
            'Ö': 'O',
            'ö': 'o',
            'ß': 'ss',
            'Ü': 'U',
            'ü': 'u',
        }

        return ''.join([character_translation[c] if c in 
            character_translation else c for c in word])
