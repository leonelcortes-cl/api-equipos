from django.shortcuts import render
from django.db import connection
from datetime import datetime, timedelta, date

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

                # ✅ Validar que no exista un registro del mismo equipo hoy
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


def dashboard(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    registros = []
    fechas = []

    if fecha_inicio and fecha_fin:
        try:
            inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if inicio > fin:
                mensaje = "⚠️ La fecha de inicio no puede ser mayor que la fecha final."
                return render(request, "dashboard.html", {"mensaje": mensaje})

            # Generar lista de fechas del rango
            delta = (fin - inicio).days
            fechas = [(inicio + timedelta(days=i)) for i in range(delta + 1)]

            # 🔹 Consultar horómetros
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT h.idTxt_Ppu, e.dtTxt_Marca, e.dtTxt_Modelo, h.dtFec_Registro, h.dtNum_Horometro
                    FROM tdHorometro h
                    JOIN tdEquipos e ON h.idTxt_Ppu = e.idTxt_Ppu
                    WHERE h.dtFec_Registro BETWEEN %s AND %s
                    ORDER BY h.idTxt_Ppu, h.dtFec_Registro
                """, [inicio, fin])
                data = cursor.fetchall()

            # 🔹 Consultar próximas mantenciones
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT idTxt_Ppu, dtNum_Proximo
                    FROM tdMantenciones
                """)
                mantenciones = dict(cursor.fetchall())

            # Organizar datos
            equipos = {}
            for ppu, marca, modelo, fecha, horometro in data:
                if ppu not in equipos:
                    equipos[ppu] = {"marca": marca, "modelo": modelo, "horometros": {}, "prox_mant": mantenciones.get(ppu)}
                equipos[ppu]["horometros"][fecha] = horometro

            # Estructurar registros
            registros = []
            for ppu, info in equipos.items():
                prox = info["prox_mant"]
                ultimo = max(info["horometros"].values()) if info["horometros"] else None
                alerta = None
                if prox and ultimo:
                    diff = prox - ultimo
                    if diff <= 0:
                        alerta = "vencida"  # rojo
                    elif diff <= 50:
                        alerta = "cercana"  # amarilla

                registros.append({
                    "ppu": ppu,
                    "marca": info["marca"],
                    "modelo": info["modelo"],
                    "prox_mant": prox,
                    "alerta": alerta,
                    "valores": [info["horometros"].get(f, "") for f in fechas],
                })

        except Exception as e:
            return render(request, "dashboard.html", {"mensaje": f"❌ Error al procesar: {e}"})

    context = {
        "fechas": fechas,
        "registros": registros,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return render(request, "dashboard.html", context)
