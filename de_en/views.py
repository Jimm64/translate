from de_en.models import GermanToEnglishDefinition
from django.shortcuts import render
from django.http import HttpResponse

import json

# Create your views here.
def translate(request):
    pass

def lookup_page(request):
    return HttpResponse('It works')

MAX_WORD_MATCH_LIMIT = 10

def get_words_matching_filter(request):
    """ Return words starting with the given filter text."""

    if not 'filter' in request.GET:
        return HttpResponse(status=422)

    if not 'limit' in request.GET:
        word_limit = 10
    else:
        try:
            word_limit = int(request.GET['limit'])
        except ValueError:
            return HttpResponse(status=422)
            
    if word_limit > MAX_WORD_MATCH_LIMIT or word_limit < 1:
        return HttpResponse(status=422)

    words_matching_filter = GermanToEnglishDefinition.objects.filter(
        word__startswith=request.GET['filter']) \
        .order_by('word')[:word_limit]

    word_results = list(map(lambda matching_word: {
        'word': matching_word.word,
        'form': matching_word.form,
        'definition': matching_word.definition}, words_matching_filter))

    return HttpResponse(json.dumps(word_results))
