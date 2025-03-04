"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path

import api.views as api

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', api.login),
    path('signup/', api.signup),

    path('get/scripts/', api.getMyScripts),
    path('get/<int:id>/', api.getScript),
    path('delete/script/<int:id>/', api.deleteScript),
    path('save/<int:scriptId>/<slug:fileName>/', api.saveFile),
    path('delete/<int:scriptId>/<slug:fileName>/', api.deleteFileFromScript),
    path('change/filename/', api.changeFileName),
    path('run/<int:id>/', api.runScript),
    path('create/', api.createScript),
    path('user/<int:id>/', api.getPublicUserInfo),
]
