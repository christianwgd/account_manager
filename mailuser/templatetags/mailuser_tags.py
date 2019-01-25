# -*- coding: utf-8 -*-

import os
from django import template
from mailuser.crypt import get_creds_filename
from mailuser.models import Account

register = template.Library()


@register.simple_tag
def f_exists(account_id):
    account = Account.objects.get(pk=account_id)
    fname = get_creds_filename(account)
    if os.path.exists(fname):
        return ''
    else:
        return ' disabled' 


