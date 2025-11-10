from django.shortcuts import render
from django.db import connection
from datetime import datetime

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
        marca, modelo = equipo
        if request.method == "POST":
            rut = request.POST.get("rut")
            horometro = request.POST.get("horometro")

            # Validar si el RUT existe en la tabla tdOperadores
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT dtTxt_Nombre, dtTxt_Apellidos
                    FROM tdOperadores
                    WHERE idNum_RUT = %s
                """, [rut])
                operador = cursor.fetchone()

            if operador:
                nombre, apellidos = operador
                # Registrar el valor en la tabla tdHorometro
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO tdHorometro (idTxt_Ppu, idNum_Rut, dtNum_Horometro, dtFec_Registro)
                        VALUES (%s, %s, %s, %s)
                    """, [codigo, rut, horometro, datetime.now().date()])

                return render(request, 'equipos/home.html', {
                    'codigo': codigo,
                    'marca': marca,
                    'modelo': modelo,
                    'existe': True,
                    'registro_exitoso': True,
                    'rut': rut,
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'horometro': horometro,
                })
            else:
                return render(request, 'equipos/home.html', {
                    'codigo': codigo,
                    'marca': marca,
                    'modelo': modelo,
                    'existe': True,
                    'error': "El RUT ingresado no pertenece a un operador autorizado."
                })

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


def dashboard(request):
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')

    registros = []
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    anios = [2023, 2024, 2025, 2026]

    if anio and mes:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT H.idTxt_Ppu, H.idNum_Rut, H.dtNum_Horometro, H.dtFec_Registro,
                       O.dtTxt_Nombre, O.dtTxt_Apellidos
                FROM tdHorometro H
                JOIN tdOperadores O ON H.idNum_Rut = O.idNum_RUT
                WHERE YEAR(H.dtFec_Registro) = %s AND MONTH(H.dtFec_Registro) = %s
                ORDER BY H.dtFec_Registro DESC
            """, [anio, mes])
            registros = cursor.fetchall()

    return render(request, 'equipos/dashboard.html', {
        'registros': registros,
        'anio': anio,
        'mes': mes,
        'anios': anios,
        'meses': meses
    })
