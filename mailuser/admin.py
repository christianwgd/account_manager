# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.html import mark_safe

from .models import Tenant, Account, Redirection


from filebrowser.settings import ADMIN_THUMBNAIL


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):

    def logo_thumbnail(self, obj):
        if obj.logo and obj.logo.filetype == "Image":
            return mark_safe('<img src="%s" />' % obj.logo.version_generate(ADMIN_THUMBNAIL).url)
        else:
            return ""

    list_display = ['name', 'domain', 'logo_thumbnail']
    ordering = ['name']
    filter_horizontal = ['manager', ]
    logo_thumbnail.allow_tags = True
    logo_thumbnail.short_description = "Logo"
    autocomplete_fields = ['manager']


@admin.register(Redirection)
class RedirectionAdmin(admin.ModelAdmin):
    list_display = ['email', 'description']


class RedirectionInlineAdmin(admin.TabularInline):
    model = Redirection
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['username', ]
    list_filter = ['tenant', ]
    ordering = ['last_name']
    change_form_template = "mailuser/custom_admin_account_change.html"
    inlines = [
        RedirectionInlineAdmin,
    ]
