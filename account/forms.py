# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.validators import FileExtensionValidator
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Account, Redirection, Tenant


class DateInput(forms.DateInput):
    input_type = 'date'


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = [
            'type', 'first_name', 'last_name',
            'username', 'description', 'def_pwd'
        ]

    def clean_username(self):
        data = self.cleaned_data['username']
        if data is None:
            raise forms.ValidationError(_('This field is required.'))
        return data


class RedirectionForm(forms.ModelForm):

    class Meta:
        model = Redirection
        fields = ['email', 'description']


class PwdForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = [
            'name', 'user', 'username',
            'first_name', 'last_name',
            'description', 'def_pwd', 'pin',
            'date', 'comment'
        ]
        widgets = {
            'date': DateInput(),
            'comment': forms.TextInput(attrs={'rows': 4})
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if data is None:
            raise forms.ValidationError(_('This field is required.'))
        return data

    
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
            'type',
            'name', 'domain', 'logo', 'weburl',
            'imap_url', 'imap_port', 'imap_sec',
            'smtp_url', 'smtp_port', 'smtp_sec',
            'man_url', 'manager',
        ]
        widgets = {
            'manager': Select2MultipleWidget
        }