# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.validators import FileExtensionValidator
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Account, Redirection, Tenant


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        exclude = ['tenant']


class RedirectionForm(forms.ModelForm):

    class Meta:
        model = Redirection
        exclude = ['account']

    
class ImportForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), label=_('tenant'))
    scheduleFile = forms.FileField(
        label='Datei',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'csv'])]
    )


class TenantForm(forms.ModelForm):

    class Meta:
        model = Tenant
        fields = [
            'name', 'domain', 'logo', 'weburl',
            'imap_url', 'imap_port', 'imap_sec',
            'smtp_url', 'smtp_port', 'smtp_sec',
            'man_url', 'manager',
        ]
        widgets = {
            'imap_sec': Select2Widget,
            'smtp_sec': Select2Widget,
            'manager': Select2MultipleWidget
        }