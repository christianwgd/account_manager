
from django.contrib import admin
from django.utils.html import mark_safe

from .models import Tenant, Account, Redirection


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):

    def logo_thumbnail(self, obj):
        if obj.logo and obj.logo.filetype == "Image":
            return mark_safe('<img src="{obj.logo.version_generate(ADMIN_THUMBNAIL).url}" />')
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
    list_display = ['get_name', 'date']
    list_filter = ['tenant', ]
    ordering = ['last_name']
    change_form_template = "account/custom_admin_account_change.html"
    readonly_fields = ['date']
    inlines = [
        RedirectionInlineAdmin,
    ]

    def get_name(self, obj):
        if obj.username:
            return obj.username
        if obj.name:
            return obj.name
        return 'no name'
