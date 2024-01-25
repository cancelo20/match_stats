from django.contrib import admin
from .models import User, Subscriptions

admin.site.register(Subscriptions)
admin.site.register(User)
