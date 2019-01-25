# -*- coding: utf-8 -*-
import os
import sys

from rfc6266 import build_header
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from .crypt import get_creds_filename, decrypt_file, init_storage_dir
from .models import Tenant, Account, Alias
from .forms import AccountForm, AliasForm


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
        messages.error(request, _("No document available for this user"))
    try:
        content = decrypt_file(fname)
    except:
        return redirect(request.META.get('HTTP_REFERER'))
    resp = HttpResponse(content)
    resp["Content-Type"] = "application/pdf"
    resp["Content-Length"] = len(content)
    resp["Content-Disposition"] = build_header(os.path.basename(fname))
    return resp


@login_required(login_url='/accounts/login/')
def tenant_list(request):
    tenants = Tenant.objects.filter(manager=request.user)
    return render(request, 'mailuser/tenant_list.html', {'tenantlist': tenants})


@login_required(login_url='/accounts/login/')
def account_list(request, tenant_id):
    tenant = Tenant.objects.get(pk=tenant_id)
    accounts = Account.objects.filter(tenant=tenant)
    return render(request, 'mailuser/account_list.html', {'accountlist': accounts, 'tenant': tenant})


@login_required(login_url='/accounts/login/')
def account_edit(request, tenant_id, account_id=None):
    if account_id is None:
        tenant = Tenant.objects.get(pk=tenant_id)
        account = Account(tenant=tenant)
        template = 'mailuser/account_new.html'
    else:
        account = Account.objects.get(pk=account_id)
        template = 'mailuser/account_edit.html'

    if request.method == 'GET':
        form = AccountForm(instance=account)
    else:
        try:
            if 'cancel' in request.POST:
                return redirect(reverse('accountlist', args=(account.tenant.id,)))

            form = AccountForm(request.POST, instance=account)
            if form.is_valid():
                form.save()
                messages.success(request, _('account changed.'))
                return redirect(reverse('accountlist', args=(account.tenant.id,)))
        except Exception as e:
            messages.error(request, _('error in edit account.'))
    return render(request, template, {
        'form': form,
        'account': account,
    })


@login_required(login_url='/accounts/login/')
def account_delete(request, account_id):

    account = Account.objects.get(pk=account_id)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('accountlist', args=(account.tenant.id,)))

        account.delete()
        messages.success(request, _(
            'Account {account} deleted.').format(account=account.username))
        return redirect(reverse('accountlist', args=(account.tenant.id,)))

    return render(request, 'mailuser/account_delete.html', {'account': account})


@login_required(login_url='/accounts/login/')
def alias_edit(request, account_id, alias_id=None):
    if alias_id is None:
        account = Account.objects.get(pk=account_id)
        alias = Alias(account=account)
    else:
        alias = Alias.objects.get(pk=alias_id)

    if 'cancel' in request.POST:
        return redirect(reverse('accountedit', args=(alias.account.tenant.id, alias.account.id,)))

    if request.method == 'GET':
        form = AliasForm(instance=alias)
    else:
        try:
            form = AliasForm(request.POST, instance=alias)
            if form.is_valid():
                form.save()
                messages.success(request, _('alias changed.'))
                return redirect(reverse('accountedit', args=(alias.account.tenant.id, alias.account.id,)))
        except Exception as e:
            messages.error(request, _('error in edit alias.'))
    return render(request, 'mailuser/alias_edit.html', {
        'form': form,
        'alias': alias,
    })


@login_required(login_url='/accounts/login/')
def alias_delete(request, alias_id):

    alias = Alias.objects.get(pk=alias_id)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('accountedit', args=(alias.account.tenant.id, alias.account.id,)))

        alias.delete()
        messages.success(request, _(
            'Alias {alias} deleted.').format(alias=alias.name))
        return redirect(reverse('accountedit', args=(alias.account.tenant.id, alias.account.id,)))

    return render(request, 'mailuser/alias_delete.html', {'alias': alias})