# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms

from .models import Account

class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = '__all__'