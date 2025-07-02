from django.contrib import admin
from .models import CustomUser, Publisher, Journalist, Article

admin.site.register(CustomUser)
admin.site.register(Publisher)
admin.site.register(Journalist)
admin.site.register(Article)
