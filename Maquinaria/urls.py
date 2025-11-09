from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('equipos', include('Equipos.urls')),  # Deriva todo hacia la app Equipos
]