"""mailuser URL Configuration

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
from django.urls import path, include
from filebrowser.sites import site
from django.conf import settings
from django.conf.urls.static import static

from . import views

admin.site.site_header = 'EHV-NRW Kontrollausschuss (KAS)'
admin.site.site_title = 'KAS'
admin.site.index_title = 'KAS Verwaltung'


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),

    path('', views.tenant_list, name='tenantlist'),
    path('tenantlist/', views.tenant_list, name='tenantlist'),
    path('accountlist/<int:tenant_id>', views.account_list, name='accountlist'),
    path('get_account_credentials/<int:account_id>/', views.get_account_credentials, name='get_account_credentials'),

    path('get_tenant_domain/<int:tenant_id>/', views.getTenantDomain, name='get_tenant_domain'),
    path('get_default_password/', views.createDefaultPassword, name='get_default_password'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
