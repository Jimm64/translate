from django.db.models.functions import Length
from de_en.models import GermanToEnglishDefinition
from django.shortcuts import render
from django.http import HttpResponse

import json

# Create your views here.
def translate(request):
    pass

def lookup_page(request):

    return render(request, 'de_en/lookup.html')

MAX_WORD_MATCH_LIMIT = 10

def get_words_matching_filter(request):
    """ Return words starting with the given filter text."""

    if not 'filter' in request.GET:
        return HttpResponse(status=422)

    filter_text = request.GET['filter']

    if not 'limit' in request.GET:
        word_limit = 10
    else:
        try:
            word_limit = int(request.GET['limit'])
        except ValueError:
            return HttpResponse(status=422)
            
    if word_limit > MAX_WORD_MATCH_LIMIT or word_limit < 1:
        return HttpResponse(status=422)

    if len(filter_text):
        filter_text = GermanToEnglishDefinition.get_search_key_for(
            filter_text)

        words_matching_filter = GermanToEnglishDefinition.objects.filter(
            search_key__startswith=filter_text) \
            .order_by('base_word_length', 'word')[:word_limit]
    else:
        words_matching_filter = []


    word_results = list(map(lambda matching_word: {
        'word': matching_word.word,
        'form': matching_word.form,
        'definition': matching_word.definition}, words_matching_filter))

    return HttpResponse(json.dumps(word_results))
