# -*- coding: utf-8 -*-
import json
import os
import sys

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, CreateView, ListView, DeleteView
from rfc6266 import build_header
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .crypt import get_creds_filename, decrypt_file
from .models import Tenant, Account, Redirection
from .forms import AccountForm, RedirectionForm, TenantForm


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


class TenantList(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'account/tenant_list.html'

    def get(self, request, *args, **kwargs):
        request.session['edit'] = request.GET.get('edit', '0')
        return super(TenantList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Tenant.objects.filter(manager=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(TenantList, self).get_context_data(**kwargs)
        ctx['edit'] = self.request.session['edit']
        return ctx


class TenantUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    success_message = _('Tenant changed')

    def get_success_url(self):
        return '{url}?edit=1'.format(
            url=reverse('tenantlist')
        )

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            messages.info(request, _('Cancelled'))
            return redirect(self.get_success_url())
        return super(TenantUpdate, self).post(request, *args, **kwargs)


class TenantCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    success_message = _('Tenant created')

    def get_success_url(self):
        return '{url}?edit=1'.format(
            url=reverse('tenantlist')
        )

    def get_initial(self):
        initial = super(TenantCreate, self).get_initial()
        initial = {"manager": self.request.user}
        return initial

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            messages.info(request, _('Cancelled'))
            return redirect(self.get_success_url())
        return super(TenantCreate, self).post(request, *args, **kwargs)


class TenantDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Tenant

    def get_success_url(self):
        return '{url}?edit=1'.format(
            url=reverse('tenantlist')
        )

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            messages.info(request, _('Cancelled'))
            return redirect(self.get_success_url())
        return super(DeleteView, self).post(request, *args, **kwargs)


@login_required(login_url='/account/login/')
def account_list(request, tenant_id):
    tenant = Tenant.objects.get(pk=tenant_id)
    accounts = Account.objects.filter(tenant=tenant).order_by('username', 'type')
    return render(request, 'account/account_list.html', {
        'accountlist': accounts,
        'tenant': tenant
    })


@login_required(login_url='/account/login/')
def account_display(request, account_id):
    account = Account.objects.get(pk=account_id)
    return render(request, 'account/account_display.html', {
        'account': account,
    })


@login_required(login_url='/account/login/')
def account_edit(request, tenant_id, account_id=None):
    if account_id is None:
        tenant = Tenant.objects.get(pk=tenant_id)
        account = Account(tenant=tenant)
        template = 'account/account_new.html'
    else:
        account = Account.objects.get(pk=account_id)
        template = 'account/account_edit.html'

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


@login_required(login_url='/account/login/')
def account_delete(request, account_id):

    account = Account.objects.get(pk=account_id)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('accountlist', args=(account.tenant.id,)))

        account.delete()
        messages.success(request, _(
            'account {account} deleted.').format(account=account.username))
        return redirect(reverse('accountlist', args=(account.tenant.id,)))

    return render(request, 'account/account_delete.html', {'account': account})


@login_required(login_url='/account/login/')
def redirect_edit(request, account_id, redirect_id=None):
    if redirect_id is None:
        account = Account.objects.get(pk=account_id)
        redirection = Redirection(account=account)
    else:
        redirection = Redirection.objects.get(pk=redirect_id)

    if 'cancel' in request.POST:
        return redirect(reverse('accountedit', args=(redirection.account.tenant.id, redirection.account.id,)))

    if request.method == 'GET':
        form = RedirectionForm(instance=redirection)
    else:
        try:
            form = RedirectionForm(request.POST, instance=redirection)
            if form.is_valid():
                form.save()
                messages.success(request, _('redirection changed.'))
                return redirect(reverse('accountedit', args=(redirection.account.tenant.id, redirection.account.id,)))
        except Exception as e:
            messages.error(request, _('error in edit redirection.'))
    return render(request, 'account/redirect_edit.html', {
        'form': form,
        'redirection': redirection,
    })


@login_required(login_url='/account/login/')
def redirect_delete(request, redirect_id):

    redirection = Redirection.objects.get(pk=redirect_id)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('accountedit', args=(redirection.account.tenant.id, redirection.account.id,)))

        redirection.delete()
        messages.success(request, _(
            'Redirection {redirection} deleted.').format(redirection=redirection.email))
        return redirect(reverse('accountedit', args=(redirection.account.tenant.id, redirection.account.id,)))

    return render(request, 'account/redirect_delete.html', {'redirection': redirection})


@login_required(login_url=' /account/login/')
def refresh_credentials(request, tenant_id):
    ''' refresh credentials for all accounts of tenant '''
    accounts = Account.objects.filter(tenant__pk=tenant_id, type='1')
    for acc in accounts:
        post_save.send(sender=Account, instance=acc)

    messages.success(request, _(
        '{count} credentials refreshed.').format(count=accounts.count()))

    if request.META.get('HTTP_REFERER') is None:
        return redirect(reverse('accountlist', args=(tenant_id,)))
    return redirect(request.META.get('HTTP_REFERER'))