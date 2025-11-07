from django.shortcuts import render, get_object_or_404
from .models import Equipo  # suponiendo que tu modelo se llama así

# Vista principal: lista de equipos
def home(request):
    equipos = Equipo.objects.all()
    return render(request, 'Equipos/equipos_form.html', {'equipos': equipos})

# Vista de detalle: muestra información de un solo equipo
def detalle_equipo(request, codigo):
    equipo = get_object_or_404(Equipo, codigo=codigo)
    return render(request, 'Equipos/detalles_equipo.html', {'equipo': equipo})
