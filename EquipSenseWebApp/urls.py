# equipment_project/urls.py
from django.conf.urls.static import static

from EquipSense import views
from EquipSenseWebApp import settings

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/equipment/'), name='home'),
    path('equipment/', include('EquipSense.urls')),
    path("register/", views.register, name="register"),
    path('accounts/', include('django.contrib.auth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)