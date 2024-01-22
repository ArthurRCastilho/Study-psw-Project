from django.contrib import admin
from .models import Categoria, Flashcard,FlashcardDesafio, Desafio

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Flashcard)
admin.site.register(FlashcardDesafio)
admin.site.register(Desafio)

