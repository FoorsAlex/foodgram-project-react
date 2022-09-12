from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active')
    filter_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_editable = ('is_active', )


admin.site.register(User, UserAdmin)
