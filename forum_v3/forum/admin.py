
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

class User(admin.ModelAdmin):
    list_display = ('username', 'status', 'role', 'email', 'get_html_avatar', 'is_active')

    def get_html_avatar(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="50px">')


admin.site.register(CustomUser, User)
admin.site.register(UserDescription)
admin.site.register(Specializations)
admin.site.register(UserSpecializations)
admin.site.register(UserEvents)
admin.site.register(Discussion)
admin.site.register(Culprits)
admin.site.register(InterlocutionTags)
