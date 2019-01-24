# -*- coding: utf-8 -*-
import os
import sys

from rfc6266 import build_header
from django.shortcuts import HttpResponse
from django.utils.crypto import get_random_string
from django.contrib import messages

from .crypt import get_creds_filename, decrypt_file, init_storage_dir
from .models import Tenant, Account


def bad_request(message):
    response = HttpResponse(json.dumps({'message': message}), 
        content_type='application/json')
    response.status_code = 400
    return response


def getTenantDomain(request, tenant_id):
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
        domain = tenant.domain
    except Tenant.DoesNotExist:
        return bad_request(message=_('No tenant selected.'))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return bad_request(message=exc_value)
    return HttpResponse(domain)


def createDefaultPassword(request):
    try:
        allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
        pw_str = get_random_string(length=12, allowed_chars=allowed_chars)
        pw = '-'.join(pw_str[i:i+3] for i in range(0, len(pw_str), 3))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return bad_request(message=exc_value)
    return HttpResponse(pw)


def get_account_credentials(request, account_id):
    """View to download a document."""
    account = Account.objects.get(pk=account_id)
    fname = get_creds_filename(account)
    if not os.path.exists(fname):
        messages.error(_("No document available for this user"))
    content = decrypt_file(fname)
    resp = HttpResponse(content)
    resp["Content-Type"] = "application/pdf"
    resp["Content-Length"] = len(content)
    resp["Content-Disposition"] = build_header(os.path.basename(fname))
    return resp