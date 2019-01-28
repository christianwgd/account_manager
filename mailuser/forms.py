# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.validators import FileExtensionValidator

from .models import Account, Alias


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        exclude = ['tenant']


class AliasForm(forms.ModelForm):

    class Meta:
        model = Alias
        exclude = ['account']

    
class ImportForm(forms.Form):
    scheduleFile = forms.FileField(
        label='Datei',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'csv'])]
    )
