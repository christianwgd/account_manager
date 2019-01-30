# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from filebrowser.fields import FileBrowseField

from .crypt import get_creds_filename, decrypt_file, init_storage_dir
from .createpdf import credentials


CONN_SECURITY = (
    ('NNE', 'None'),
    ('SSL', 'SSL'),
    ('TLS', 'TLS'),
    ('STL', 'SSL/TLS'),
    ('STL', 'STARTTLS'),
)

class Tenant(models.Model):
    
    def __str__(self):
        return self.name

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
    smtp_port = models.CharField(_('SMTP server port'), max_length=3, default='25')
    smtp_sec = models.CharField(_('SMTP connection security'), max_length=3, choices=CONN_SECURITY, default='NNE')
    imap_url = models.CharField(_('IMAP server address'), max_length=50, null=True, blank=True)
    imap_port = models.CharField(_('IMAP server port'), max_length=3, default='143')
    imap_sec = models.CharField(_('IMAP connection security'), max_length=3, choices=CONN_SECURITY, default='NNE')
    man_url = models.URLField(_('manual url'), null=True, blank=True)
    manager = models.ManyToManyField(User, verbose_name=_('manager'))


ACCOUNT_TYPE = (
    ('1', _('account')),
    ('2', _('redirection')),
)

class Account(models.Model):
    
    def __str__(self):
        return self.username

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
        unique_together = ('type', 'username',)

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name=_('tenant'))
    type = models.CharField(_('account type'), max_length=1, choices=ACCOUNT_TYPE, default='1')
    first_name = models.CharField(_('first name'), max_length=50, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)
    username = models.EmailField(_('account user'))
    description = models.CharField(_('description'), max_length=80, null=True, blank=True)
    def_pwd = models.CharField(_('default password'), max_length=50, null=True, blank=True)


@receiver(post_save, sender=Account)
def account_updated(sender, **kwargs):
    """Create or update account."""
    account = kwargs['instance']
    init_storage_dir()
    credentials(account)


class Redirection(models.Model):
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('redirection')
        verbose_name_plural = _('redirections')
        ordering = ['email']

    email =  models.EmailField(_('email'))
    description = models.CharField(_('description'), max_length=80, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_('account'))