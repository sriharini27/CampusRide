from django.contrib import admin
from django.urls import path, include

handler404 = 'transport.views.custom_404_view'
handler403 = 'transport.views.custom_403_view'
handler500 = 'transport.views.custom_500_view'

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('transport.urls')),
]
