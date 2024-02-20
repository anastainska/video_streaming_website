from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Admin, Subscriber, Show, Folder

# Register your models here.


class SubscriberAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Show)
admin.site.register(Folder)
