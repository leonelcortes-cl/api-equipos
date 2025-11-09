from django.shortcuts import render
from django.db import connection

def home(request, codigo):
    # Buscar el equipo por su código (idTxt_Ppu)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dtTxt_Marca, dtTxt_Modelo
            FROM tdEquipos
            WHERE idTxt_Ppu = %s
        """, [codigo])
        equipo = cursor.fetchone()

    if equipo:
        # Desempaquetar los valores de la tupla
        marca, modelo = equipo
        return render(request, 'equipos/home.html', {
            'codigo': codigo,
            'marca': marca,
            'modelo': modelo,
            'existe': True
        })
    else:
        return render(request, 'equipos/home.html', {
            'codigo': codigo,
            'existe': False
        })
