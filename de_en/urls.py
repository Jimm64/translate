from django.contrib import admin
from django.urls import path
from de_en import views

urlpatterns = [
    path('', views.lookup_page),
]
