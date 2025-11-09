from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Vista temporal para verificar que el sitio responde
def home(request):
    return HttpResponse("API de Equipos activa")

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Página raíz opcional (por si alguien entra a la raíz del dominio)
    path('', home),

    # Módulo de Equipos con prefijo /equipos/
    path('equipos/', include('Equipos.urls')),
]
