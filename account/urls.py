"""account URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from filebrowser.sites import site
from django.conf import settings
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views

from account import views
from account import file_import
from two_factor.urls import urlpatterns as tf_urls

admin.site.site_header = _('Account Manager')


urlpatterns = [
    path('', include(tf_urls)),
    path('admin/filebrowser/', site.urls),
    path('accounts/login/', RedirectView.as_view(url='/account/login/')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),

    path('', views.TenantList.as_view(), name='tenantlist'),
    path('tenantlist/', views.TenantList.as_view(), name='tenantlist'),
    path('tenantadd/', views.TenantCreate.as_view(), name='tenantadd'),
    path('tenantedit/<int:pk>/', views.TenantUpdate.as_view(), name='tenantedit'),
    path('tenantdelete/<int:pk>/', views.TenantDelete.as_view(), name='tenantdelete'),

    path('accountlist/<int:tenant_id>/', views.account_list, name='accountlist'),
    path('accountdisplay/<int:account_id>/', views.account_display, name='accountdisplay'),
    path('accountedit/<int:tenant_id>/', views.account_edit, name='accountnew'),
    path('accountedit/<int:tenant_id>/<int:account_id>/', views.account_edit, name='accountedit'),
    path('accountdelete/<int:account_id>/', views.account_delete, name='accountdelete'),

    path('redirectedit/<int:account_id>/', views.redirect_edit, name='redirectnew'),
    path('redirectedit/<int:account_id>/<int:redirect_id>/', views.redirect_edit, name='redirectedit'),
    path('redirectdelete/<int:redirect_id>/', views.redirect_delete, name='redirectdelete'),
    path('get_account_credentials/<int:account_id>/', views.get_account_credentials, name='get_account_credentials'),
    path('refreshcredentials/<int:tenant_id>/', views.refresh_credentials, name='refreshcredentials'),
    
    path('pwdlist/<int:tenant_id>/', views.PwdList.as_view(), name='pwdlist'),
    path('pwddetail/<int:pk>/', views.PwdDetail.as_view(), name='pwddetail'),
    path('pwdcreate/<int:tenant_id>/', views.PwdCreate.as_view(), name='pwdcreate'),
    path('pwdupdate/<int:pk>/', views.PwdUpdate.as_view(), name='pwdupdate'),

    path('get_tenant_domain/<int:tenant_id>/', views.get_tenant_domain, name='get_tenant_domain'),
    path('get_default_password/', views.create_default_password, name='get_default_password'),

    path('import/', file_import.importFromFile, name='import'),

    path(
        'pwd_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='account/password_change_form.html',
            success_url=reverse_lazy('pwd_change_done')
        ),
        name='pwd_change'
    ),
    path(
        'pwd_change_done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='account/password_change_done_form.html'
        ),
        name='pwd_change_done'
    ),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
