from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

def buscar_equipo(request, codigo):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tdEquipos WHERE idTxt_Ppu = %s", [codigo])
        resultado = cursor.fetchone()

    if resultado:
        return HttpResponse(f"✅ Equipo encontrado: {resultado}")
    else:
        return HttpResponse("❌ No existe ningún equipo con ese código.")
