from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import TdEquipos  # Ajusta el nombre del modelo si difiere

def equipo_detalle(request, codigo):
    equipo = get_object_or_404(TdEquipos, idTxt_Ppu=codigo)
    
    # Si el request pide JSON (por otra app o API), devolvemos JSON
    if request.headers.get('Accept') == 'application/json':
        data = {
            "idTxt_Ppu": equipo.idTxt_Ppu,
            "idNum_Propietario": equipo.idNum_Propietario,
            "idNum_Tipo": equipo.idNum_Tipo,
            "dtFec_Anio": equipo.dtFec_Anio,
            "dtTxt_Marca": equipo.dtTxt_Marca,
            "dtTxt_Modelo": equipo.dtTxt_Modelo,
            "dtTxt_Chasis": equipo.dtTxt_Chasis,
            "dtTxt_Motor": equipo.dtTxt_Motor,
        }
        return JsonResponse(data)
    
    # Si se abre desde un navegador, devolvemos HTML
    return render(request, "equipos/detalle_equipo.html", {"equipo": equipo})
