# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from filebrowser.fields import FileBrowseField


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

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name=_('tenant'))
    first_name = models.CharField(_('first name'), max_length=50, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)
    username = models.EmailField(_('account user'))
    description = models.CharField(_('description'), max_length=80, null=True, blank=True)
    def_pwd = models.CharField(_('default password'), max_length=50)


class Alias(models.Model):
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('mail alias')
        verbose_name_plural = _('mail aliases')
        ordering = ['name']

    name =  models.EmailField(_('alias'))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_('Account'))