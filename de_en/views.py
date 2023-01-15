from de_en.models import GermanToEnglishDefinition
from django.shortcuts import render
from django.http import HttpResponse

import json

# Create your views here.
def translate(request):
    pass

def lookup_page(request):
    return HttpResponse('It works')

def get_words_matching_filter(request):
    """ Return words starting with the given filter text."""

    if not 'filter' in request.GET:
        return HttpResponse(status=422)

    words_matching_filter = GermanToEnglishDefinition.objects.filter(
        word__startswith=request.GET['filter'])

    word_results = list(map(lambda matching_word: {
        'word': matching_word.word,
        'form': matching_word.form,
        'definition': matching_word.definition}, words_matching_filter))

    return HttpResponse(json.dumps(word_results))
