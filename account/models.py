# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from filebrowser.fields import FileBrowseField

from .crypt import init_storage_dir
from .createpdf import credentials
from .password_pdf import password_credentials


def user_str_patch(self):
    if self.first_name and self.last_name:
        name = self.get_full_name()
    else:
        name = self.username
    return name


User.__str__ = user_str_patch

CONN_SECURITY = (
    ('NNE', 'None'),
    ('SSL', 'SSL'),
    ('TLS', 'TLS'),
    ('SST', 'SSL/TLS'),
    ('STS', 'STARTTLS'),
)

TENANT_TYPE = (
    ('mail', _('mail accounts')),
    ('othr', _('passwords')),
)


class Tenant(models.Model):

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return 'Tenant'

    class Meta:
        verbose_name = _('mail tenant')
        verbose_name_plural = _('mail tenants')
        ordering = ['name']

    name = models.CharField(_('name'), max_length=50, null=True, blank=True)
    domain = models.CharField(_('domain'), max_length=50, null=True, blank=True)
    logo = FileBrowseField(_('Logo'), max_length=200, directory='logos/',
                           extensions=['.jpg', '.png'], blank=True)
    weburl = models.URLField(_('web url'), null=True, blank=True)
    smtp_url = models.CharField(_('SMTP server address'), max_length=50, null=True, blank=True)
    smtp_port = models.CharField(_('SMTP server port'), max_length=3, default='465')
    smtp_sec = models.CharField(_('SMTP connection security'), max_length=3, choices=CONN_SECURITY, default='SST')
    imap_url = models.CharField(_('IMAP server address'), max_length=50, null=True, blank=True)
    imap_port = models.CharField(_('IMAP server port'), max_length=3, default='993')
    imap_sec = models.CharField(_('IMAP connection security'), max_length=3, choices=CONN_SECURITY, default='SST')
    man_url = models.URLField(_('manual url'), null=True, blank=True)
    manager = models.ManyToManyField(User, verbose_name=_('manager'))
    type = models.CharField(_('Type'), max_length=4, choices=TENANT_TYPE, default='mail')


ACCOUNT_TYPE = (
    ('1', _('account')),
    ('2', _('alias')),
    ('3', _('password')),
)


class Account(models.Model):

    def __str__(self):
        if self.username:
            return self.username
        else:
            if self.name:
                return self.name
            else:
                return 'no name'

    @property
    def full_name(self):
        if self.first_name is not None and self.last_name is not None:
            return self.first_name + ' ' + self.last_name
        else:
            return None

    class Meta:
        verbose_name = _('mail account')
        verbose_name_plural = _('mail accounts')
        ordering = ['last_name']

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name=_('tenant'))
    type = models.CharField(_('account type'), max_length=1, choices=ACCOUNT_TYPE, default='1')
    first_name = models.CharField(_('first name'), max_length=50, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)
    username = models.EmailField(_('email'), null=True, blank=True)
    description = models.CharField(_('description'), max_length=80, null=True, blank=True)
    def_pwd = models.CharField(_('default password'), max_length=50, null=True, blank=True)
    # Other accounts
    name = models.CharField(_('name'), max_length=50, null=True, blank=True)
    user = models.CharField(_('username'), max_length=50, null=True, blank=True)
    date = models.DateField(_('date'), null=True, blank=True)
    comment = models.TextField(_('comment'), null=True, blank=True)
    pin = models.CharField(_('PIN'), max_length=10, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()
        return super().save(*args, **kwargs)


@receiver(post_save, sender=Account)
def account_updated(sender, **kwargs):
    """Create or update account."""
    account = kwargs['instance']
    init_storage_dir()
    if account.type == '3':
        password_credentials(account)
    else:
        credentials(account)



class Redirection(models.Model):

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('redirection')
        verbose_name_plural = _('redirections')
        ordering = ['email']

    email = models.EmailField(_('email'))
    description = models.CharField(_('description'), max_length=80, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_('account'))
