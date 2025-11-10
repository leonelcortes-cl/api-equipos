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

    meses = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    registros = []
    mes_nombre = None

    if anio and mes:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT idTxt_Ppu, idNum_RUT, dtNum_Horometro, dtFec_Registro
                FROM tdHorometro 
                WHERE YEAR(dtFec_Registro) = %s AND MONTH(dtFec_Registro) = %s
                ORDER BY dtFec_Registro DESC
            """, [anio, mes])
            registros = cursor.fetchall()
        mes_nombre = meses.get(mes.zfill(2), "")

    # Años disponibles para el filtro
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT YEAR(dtFec_Registro) FROM tdHorometro ORDER BY 1 DESC")
        anios = [row[0] for row in cursor.fetchall()]

    return render(request, 'equipos/dashboard.html', {
        'registros': registros,
        'anios': anios,
        'meses': meses,
        'anio': anio,
        'mes': mes,
        'mes_nombre': mes_nombre,
    })

