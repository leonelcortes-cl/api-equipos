from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Módulo de Equipos con prefijo /equipos/
    path('equipos/', include('Equipos.urls')),
]
