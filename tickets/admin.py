from django.contrib import admin
from .models import Category, Ticket, Comment, CustomUser

from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Category)
admin.site.register(Ticket)
admin.site.register(Comment)
