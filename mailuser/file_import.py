# encoding: utf-8

import codecs
import os
import datetime
import json
import csv

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core import serializers
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from .models import Account, Tenant
from .forms import ImportForm


@login_required(login_url='/accounts/login/')
def importFromFile(request):

    accounts = []

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
                # TODO: set tenant either from URL or from Form!
                tenant = Tenant.objects.get(pk='1')
                filepath = 'static/media/imports/'
                schedFile = request.FILES['scheduleFile']
                fs = FileSystemStorage(location=filepath)
                filename = fs.save(schedFile.name, schedFile)
                fullfile = '{}/{}'.format(filepath, filename)
                enc = 'utf-8'
                # enc = 'cp1252'
                f = codecs.open(fullfile, 'r', encoding=enc)
                reader = csv.reader(f, delimiter=';', quotechar='"')
                
                for row in reader:
                    if row[MBTYPE] == 'account':
                        account = Account(
                            tenant=tenant,
                            username = row[USRNAME],
                            first_name = row[FSTNAME],
                            last_name = row[LSTNAME],
                            redirect = False
                        )
                    elif row[MBTYPE] == 'alias':
                        account = Account(
                            tenant=tenant,
                            username = row[USRNAME],
                            redirect = True
                        )
                        alias_col = REDIRECT
                        try:
                            while row[alias_col]:
                                user
                                alias_col += 1
                        except:
                            pass
                    else:
                        print('invalid type')
                    accounts.append(account)

                f.close()
                dump_accounts(accounts)
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

    return render(request, 'mailuser/import.html', {
        'form': form,
        'accounts': accounts,
    })


def dump_accounts(accounts):
    filename = '{}/imports/import.json'.format(settings.MEDIA_ROOT)
    exportdata = {}
    exportdata['accounts'] = []
    for acc in accounts:
        exportdata['accounts'].append(acc.attrs_as_json())
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

        count = len(jsondata['accounts'])
        for acc in jsondata['accounts']:
            print('######################', acc, '######################')
            t = Account(
                # team = Team.objects.get(pk=event['team']),
                # ort = Spielort.objects.get(pk=event['ort']),
                # gegner = Gegner.objects.get(pk=event['gegner']),
                # datum = date,
                # von = tz.localize(datetime.datetime.strptime(event['von'], '%H:%M')),
                # bis = tz.localize(datetime.datetime.strptime(event['bis'], '%H:%M')),
                # kw = date.isocalendar()[1],
                # typ = event['typ'],
                # status = event['status'],
                # version = 0,
                # league = True,
                # bemerkung = '',
                # coach = Player.objects.get(team=event['team'], role__key='C').person,
            )
            #t.save()
        infile.close()
        return count