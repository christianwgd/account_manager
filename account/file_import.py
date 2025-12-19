
import codecs
import json
import csv
from pathlib import Path

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
def import_from_file(request):

    accounts = {}

    mbtype = 0
    usrname = 1
    fstname = 3
    lstname = 4
    redrct = 3


    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('tenantlist'))

        if 'import' in request.POST:
            count = load_accounts()
            if count is None:
                messages.info(request, _('No accounts created').format(count))
            else:
                messages.success(request, f'{count} accounts created')
            return redirect(reverse('tenantlist'))


        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            accounts = []
            tenant = form.cleaned_data['tenant']
            sched_file = request.FILES['schedule_file']
            fs = FileSystemStorage(location='imports/')
            filename = fs.save(sched_file.name, sched_file)
            enc = 'utf-8'
            # enc = 'cp1252'
            with codecs.open(filename, 'r', encoding=enc) as f:
                reader = csv.reader(f, delimiter=';', quotechar='"')

                for row in reader:
                    if row[mbtype] == 'account':
                        account = {
                            'type': '1',
                            'tenant': tenant.id,
                            'username': row[usrname],
                            'first_name': row[fstname],
                            'last_name': row[lstname],
                        }
                    elif row[mbtype] == 'alias':
                        account = {
                            'type': '2',
                            'tenant': tenant.id,
                            'username': row[usrname],
                        }
                        alias_col = redrct
                        try:
                            redirections = []
                            while row[alias_col]:
                                redirections.append(row[alias_col])
                                alias_col += 1
                        except IndexError:
                            pass
                        account['redirections'] = redirections
                    accounts.append(account)

            f.close()
            dump_accounts(accounts, tenant.id)
            # if os.path.exists(fullfile):
            #     os.remove(fullfile)

    else:  # GET
        try:
            form = ImportForm()
        except Exception as exc:
            messages.error(request, f'Error {exc}')

    return render(request, 'account/import.html', {
        'form': form,
        'accounts': accounts,
    })


def dump_accounts(accounts, tenant):
    filename = Path(f'{settings.MEDIA_ROOT}/imports/import.json')
    exportdata = {'tenant': tenant, 'accounts': accounts}

    with Path.open(filename, 'w') as outfile:
        outfile.write(json.dumps(exportdata, indent=4))
    outfile.close()


@transaction.atomic
def load_accounts():
    filename = Path(f'{settings.MEDIA_ROOT}/imports/import.json')
    if filename.exists():
        with Path.open(filename) as infile:
            importdata = infile.read()

        jsondata = json.loads(importdata)
        if len(jsondata['accounts']) == 0:
            return None

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
    return 0
