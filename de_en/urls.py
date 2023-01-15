from django.contrib import admin
from django.urls import path
from de_en import views

urlpatterns = [
    path('', views.lookup_page),
    path('filter', views.get_words_matching_filter, name='filter'),
]
