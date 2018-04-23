"""ansibleAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from API import views

from API.AnsibleView import AnsibleViewSet
from API.PmsdView import PmsdView
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'^ansible/web_api/v1_0', AnsibleViewSet, base_name=r'^ansible/web_api/v1_0')
router.register(r'^pms',PmsdView,base_name=r'^pms')
urlpatterns = router.urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^ansible/web_api/v1_0/auth',views.auth),
    #url(r'^ansible/web_api/v1_0/run',views.run),
    #url(r'^ansible/web_api/v1_0/upload_script',views.upload),
    #url(r'^ansible/web_api/v1_0/copy_file',views.copy),
    url(r'^',include(router.urls)),
]
