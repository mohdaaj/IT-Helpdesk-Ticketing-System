from django.contrib import admin
from .models import Category, Ticket, Comment, MyUser, Notification

from django.contrib.auth.admin import UserAdmin

admin.site.register(MyUser, UserAdmin)
admin.site.register(Category)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Notification)
