from django.contrib import admin
from .models import Equipment, Request, Category, Tag

# Register your models here.
admin.site.register(Equipment)
admin.site.register(Request)
admin.site.register(Category)
admin.site.register(Tag)
