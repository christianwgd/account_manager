from pathlib import Path

from django import template
from account.crypt import get_creds_filename
from account.models import Account

register = template.Library()


@register.simple_tag
def f_exists(account_id):
    account = Account.objects.get(pk=account_id)
    fname = get_creds_filename(account)
    if Path(fname).exists():
        return ''
    return ' disabled'


