from django.shortcuts import render
from django.db import connection

def home(request, codigo):
    # Buscar el equipo por código
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tdEquipos WHERE idTxt_Ppu = %s", [codigo])
        equipo = cursor.fetchone()

    # Validar existencia
    if equipo:
        # Si el código existe, mostrar el formulario
        return render(request, 'equipos/home.html', {'codigo': codigo, 'existe': True})
    else:
        # Si no existe, mostrar mensaje de error
        return render(request, 'equipos/home.html', {'codigo': codigo, 'existe': False})
