from django.contrib import admin
from .models import Category, Ticket, MyUser, Notification

from django.contrib.auth.admin import UserAdmin

admin.site.register(MyUser, UserAdmin)
admin.site.register(Category)
admin.site.register(Ticket)

admin.site.register(Notification)
