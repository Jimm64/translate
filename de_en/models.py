from django.db import models

# Create your models here.
class GermanToEnglishDefinition(models.Model):

    word = models.CharField(max_length=64) 
    form = models.CharField(max_length=32,null=True)
    definition = models.CharField(max_length=256)

