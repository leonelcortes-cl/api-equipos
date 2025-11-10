from django.shortcuts import render
from django.db import connection
from datetime import date

def dashboard(request):
    registros = []
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')

    # Si se seleccionó año y mes
    if anio and mes:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    H.dtFec_Registro,
                    H.idTxt_Ppu,
                    E.dtTxt_Marca,
                    E.dtTxt_Modelo,
                    H.idNum_Rut,
                    O.dtTxt_Nombre,
                    O.dtTxt_Apellidos,
                    H.dtNum_Horometro
                FROM tdHorometro H
                LEFT JOIN tdEquipos E ON H.idTxt_Ppu = E.idTxt_Ppu
                LEFT JOIN tdOperadores O ON H.idNum_Rut = O.idNum_RUT
                WHERE YEAR(H.dtFec_Registro) = %s AND MONTH(H.dtFec_Registro) = %s
                ORDER BY H.dtFec_Registro DESC
            """, [anio, mes])
            registros = cursor.fetchall()

    # Enviar datos a la plantilla
    return render(request, 'equipos/dashboard.html', {
        'registros': registros,
        'anio': anio,
        'mes': mes
    })


def home(request, codigo):
    mensaje = None
    datos_registro = None

    # Buscar equipo por su código (idTxt_Ppu)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dtTxt_Marca, dtTxt_Modelo
            FROM tdEquipos
            WHERE idTxt_Ppu = %s
        """, [codigo])
        equipo = cursor.fetchone()

    if equipo:
        marca, modelo = equipo
        existe = True
    else:
        marca = modelo = None
        existe = False

    # Si se envió el formulario (con RUT y horómetro)
    if request.method == "POST":
        rut = request.POST.get("rut")
        horometro = request.POST.get("horometro")

        # Validar que el operador exista
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT dtTxt_Nombre, dtTxt_Apellidos
                FROM tdOperadores
                WHERE idNum_RUT = %s
            """, [rut])
            operador = cursor.fetchone()

        if operador:
            nombre, apellidos = operador
            # Guardar el registro en tdHorometro
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tdHorometro (idTxt_Ppu, idNum_Rut, dtNum_Horometro, dtFec_Registro)
                    VALUES (%s, %s, %s, %s)
                """, [codigo, rut, horometro, date.today()])

            mensaje = "Registro guardado exitosamente."
            datos_registro = {
                "codigo": codigo,
                "nombre": nombre,
                "apellidos": apellidos,
                "horometro": horometro,
                "fecha": date.today().strftime("%d-%m-%Y")
            }
        else:
            mensaje = "❌ RUT no autorizado para operar este equipo."
    
    return render(request, 'equipos/home.html', {
        'codigo': codigo,
        'marca': marca,
        'modelo': modelo,
        'existe': existe,
        'mensaje': mensaje,
        'datos_registro': datos_registro
    })
