from django.contrib import admin

from .models import *

admin.site.register(Client)
admin.site.register(Directory)
admin.site.register(Content)
admin.site.register(LoginAttempt)

