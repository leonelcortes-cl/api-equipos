from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Equipos.urls')),  # Deriva todo hacia la app Equipos
]
