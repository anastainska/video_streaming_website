from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import *


class SubscriberAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    ordering = '-date_joined',

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


class ShowAdmin(admin.ModelAdmin):
    list_display = ['title', 'show_type', 'year', 'category']
    list_filter = ['show_type', 'category']
    search_fields = ['title', 'description']
    fields = ('title', 'description', 'year', 'poster', 'category', 'show_type', 'video')


class SubscriberProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture:
            return format_html(
                '<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
        else:
            return "No profile picture available"

    thumbnail.allow_tags = True
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user')


admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(Folder)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ReviewRating)
admin.site.register(SubscriberProfile, SubscriberProfileAdmin)
admin.site.register(Season)
admin.site.register(Episode)
