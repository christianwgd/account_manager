# encoding: utf-8

import codecs
import os
import json
import csv

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .models import Account, Tenant, Redirection
from .forms import ImportForm


@login_required(login_url='/accounts/login/')
def importFromFile(request):

    accounts = {}

    MBTYPE = 0
    USRNAME = 1

    FSTNAME = 3
    LSTNAME = 4

    REDIRECT = 3
    

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('tenantlist'))

        if 'import' in request.POST:
            count = load_accounts()
            if count is None:
                messages.info(request, _('No accounts created').format(count))
            else:
                messages.success(request, '{} accounts created'.format(count))
            return redirect(reverse('tenantlist'))
    

        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                accounts = []
                tenant = form.cleaned_data['tenant']
                schedFile = request.FILES['scheduleFile']
                fs = FileSystemStorage(location='imports/')
                filename = fs.save(schedFile.name, schedFile)
                enc = 'utf-8'
                # enc = 'cp1252'
                f = codecs.open(filename, 'r', encoding=enc)
                reader = csv.reader(f, delimiter=';', quotechar='"')
                
                for row in reader:
                    if row[MBTYPE] == 'account':
                        account = {
                            'type': '1',
                            'tenant': tenant.id,
                            'username': row[USRNAME],
                            'first_name': row[FSTNAME],
                            'last_name': row[LSTNAME],
                        }
                    elif row[MBTYPE] == 'alias':
                        account = {
                            'type': '2',
                            'tenant': tenant.id,
                            'username': row[USRNAME],
                        }
                        alias_col = REDIRECT
                        try:
                            redirections = []
                            while row[alias_col]:
                                redirections.append(row[alias_col])
                                alias_col += 1
                        except IndexError:
                            pass
                        account['redirections'] = redirections
                    else:
                        print('invalid type')
                    accounts.append(account)

                f.close()
                dump_accounts(accounts, tenant.id)
                # if os.path.exists(fullfile):
                #     os.remove(fullfile)
            except:
                import traceback
                traceback.print_exc()

    else:  # GET
        try:
            form = ImportForm()
        except Exception as exc:
            messages.error(request, u'Error %s' % exc)

    return render(request, 'account/import.html', {
        'form': form,
        'accounts': accounts,
    })


def dump_accounts(accounts, tenant):
    filename = '{}/imports/import.json'.format(settings.MEDIA_ROOT)
    exportdata = {}

    exportdata['tenant'] = tenant
    exportdata['accounts'] = accounts

    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(exportdata, indent=4))
    outfile.close()


@transaction.atomic
def load_accounts():
    filename = '{}/imports/import.json'.format(settings.MEDIA_ROOT)
    if os.path.exists(filename):
        with open(filename, 'r') as infile:
            importdata = infile.read()

        jsondata = json.loads(importdata)
        if len(jsondata['accounts']) == 0:
            return

        tenant = Tenant.objects.get(pk=jsondata['tenant'])
        count = len(jsondata['accounts'])
        for acc in jsondata['accounts']:
            if acc['type'] == '1':
                account = Account(
                    tenant = tenant,
                    type = acc['type'], 
                    username = acc['username'],
                    first_name = acc['first_name'],
                    last_name = acc['last_name'],
                )
                account.save()
            else:
                account = Account(
                    tenant = tenant,
                    type = acc['type'], 
                    username = acc['username'],
                )
                account.save()
                for red in acc['redirections']:
                    redirection = Redirection(
                        account = account,
                        email = red,
                    )
                    redirection.save()
        infile.close()
        return count