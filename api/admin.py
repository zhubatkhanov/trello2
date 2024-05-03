from django.contrib import admin
from .models import User, Board, ListCard, Card


admin.site.register(User)
admin.site.register(Board)
admin.site.register(ListCard)
admin.site.register(Card)
