# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Tenant, Account, Alias

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain']
    ordering = ['name']


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ['name', ]


class AliasInlineAdmin(admin.TabularInline):
    model = Alias
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['username', ]
    list_filter = ['tenant', ]
    ordering = ['last_name']
    change_form_template = "mailuser/custom_admin_account_change.html"
    inlines = [
        AliasInlineAdmin,
    ]
