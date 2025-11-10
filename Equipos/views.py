from django.shortcuts import render
from django.db import connection
from datetime import datetime, timedelta

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
        rut = request.POST.get("rut", "").strip()
        horometro = request.POST.get("horometro", "").strip()

        # ✅ Validación 1: campos vacíos
        if not rut or not horometro:
            mensaje = "⚠️ Debe ingresar el RUT y el valor del horómetro."
        # ✅ Validación 2: horómetro debe ser numérico y no negativo
        elif not horometro.isdigit() or int(horometro) < 0:
            mensaje = "❌ Valor de horómetro inválido."
        else:
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

                # ✅ Validar que no exista un registro del mismo operador/equipo hoy
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM tdHorometro
                        WHERE idTxt_Ppu = %s AND dtFec_Registro = %s
                    """, [codigo, date.today()])
                    existe_registro = cursor.fetchone()[0] > 0

                if existe_registro:
                    mensaje = "⚠️ Ya existe un registro para este equipo hoy."
                else:
                    # Guardar el registro en tdHorometro
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO tdHorometro (idTxt_Ppu, idNum_Rut, dtNum_Horometro, dtFec_Registro)
                            VALUES (%s, %s, %s, %s)
                        """, [codigo, rut, int(horometro), date.today()])

                    mensaje = "✅ Registro guardado exitosamente."
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

from django.shortcuts import render
from django.db import connection
from datetime import datetime, timedelta

def dashboard(request):
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    registros = []
    columnas_fechas = []
    tabla = []

    if fecha_inicio and fecha_fin:
        try:
            # Convertir fechas a objetos datetime
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            # Obtener todas las fechas del rango
            columnas_fechas = [(inicio + timedelta(days=i)) for i in range((fin - inicio).days + 1)]

            with connection.cursor() as cursor:
                # Obtener todos los equipos con sus lecturas dentro del rango
                cursor.execute("""
                    SELECT h.idTxt_Ppu, e.dtTxt_Marca, e.dtTxt_Modelo, h.dtFec_Registro, h.dtNum_Horometro
                    FROM tdHorometro h
                    JOIN tdEquipos e ON h.idTxt_Ppu = e.idTxt_Ppu
                    WHERE h.dtFec_Registro BETWEEN %s AND %s
                    ORDER BY h.idTxt_Ppu, h.dtFec_Registro
                """, [inicio, fin])
                registros = cursor.fetchall()

            # Reorganizar registros en formato {ppu: {fecha: horometro}}
            data_por_equipo = {}
            for ppu, marca, modelo, fecha, horometro in registros:
                if ppu not in data_por_equipo:
                    data_por_equipo[ppu] = {
                        'marca': marca,
                        'modelo': modelo,
                        'lecturas': {}
                    }
                data_por_equipo[ppu]['lecturas'][fecha] = horometro

            # Construir la tabla final
            for ppu, datos in data_por_equipo.items():
                fila = [ppu, datos['marca'], datos['modelo']]
                for fecha in columnas_fechas:
                    valor = datos['lecturas'].get(fecha)
                    fila.append(valor if valor is not None else "")
                tabla.append(fila)

        except ValueError:
            registros = []
            columnas_fechas = []
            tabla = []

    return render(request, 'equipos/dashboard.html', {
        'tabla': tabla,
        'columnas_fechas': columnas_fechas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })
