from django.shortcuts import render
from django.db import connection
from datetime import datetime, timedelta, date
"""
from django.http import HttpResponse
import qrcode
from io import BytesIO
import openpyxl
from .models import QRCode
"""

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
    
    return render(request, 'home.html', {
        'codigo': codigo,
        'marca': marca,
        'modelo': modelo,
        'existe': existe,
        'mensaje': mensaje,
        'datos_registro': datos_registro
    })

def registro_manual(request):
    mensaje = None
    datos_registro = None
    marca = modelo = None
    existe = False

    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip().upper()
        rut = request.POST.get("rut", "").strip()
        horometro = request.POST.get("horometro", "").strip()

        # ✅ Validación 1: campos vacíos
        if not codigo or not rut or not horometro:
            mensaje = "⚠️ Debe ingresar el código del equipo, el RUT y el valor del horómetro."
        # ✅ Validación 2: horómetro debe ser numérico y no negativo
        elif not horometro.isdigit() or int(horometro) < 0:
            mensaje = "❌ Valor de horómetro inválido."
        else:
            # Buscar equipo
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

                # Validar operador
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT dtTxt_Nombre, dtTxt_Apellidos
                        FROM tdOperadores
                        WHERE idNum_RUT = %s
                    """, [rut])
                    operador = cursor.fetchone()

                if operador:
                    nombre, apellidos = operador

                    # Validar que no exista un registro del mismo equipo hoy
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) FROM tdHorometro
                            WHERE idTxt_Ppu = %s AND dtFec_Registro = %s
                        """, [codigo, date.today()])
                        existe_registro = cursor.fetchone()[0] > 0

                    if existe_registro:
                        mensaje = "⚠️ Ya existe un registro para este equipo hoy."
                    else:
                        # Guardar registro
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
            else:
                mensaje = "❌ No existe un equipo con ese código."

    return render(request, 'manual.html', {
        'mensaje': mensaje,
        'datos_registro': datos_registro,
        'existe': existe,
        'marca': marca,
        'modelo': modelo
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

            with connection.cursor() as cursor:
                # Obtener datos de horómetro + datos del equipo + próxima mantención
                cursor.execute("""
                    SELECT 
                        h.idTxt_Ppu,
                        e.dtTxt_Marca,
                        e.dtTxt_Modelo,
                        h.dtFec_Registro,
                        h.dtNum_Horometro,
                        m.dtNum_Proximo
                    FROM tdHorometro h
                    JOIN tdEquipos e ON h.idTxt_Ppu = e.idTxt_Ppu
                    LEFT JOIN tdMantenciones m ON h.idTxt_Ppu = m.idTxt_Ppu
                    WHERE h.dtFec_Registro BETWEEN %s AND %s
                    ORDER BY h.idTxt_Ppu, h.dtFec_Registro
                """, [inicio, fin])
                data = cursor.fetchall()

                # Obtener último horómetro por equipo (parche seguro)
                cursor.execute("""
                    SELECT h1.idTxt_Ppu, h1.dtNum_Horometro
                    FROM tdHorometro h1
                    INNER JOIN (
                        SELECT idTxt_Ppu, MAX(dtFec_Registro) AS ultima
                        FROM tdHorometro
                        GROUP BY idTxt_Ppu
                    ) h2 ON h1.idTxt_Ppu = h2.idTxt_Ppu AND h1.dtFec_Registro = h2.ultima
                """)

                ultimos_raw = cursor.fetchall()
                ultimos = {}

                # Parche para evitar errores de None + drivers de cPanel
                for row in ultimos_raw:
                    if row and row[0] is not None and row[1] is not None:
                        ultimos[row[0]] = row[1]

            # Organizar datos por equipo
            equipos = {}
            for ppu, marca, modelo, fecha, horometro, prox_mant in data:
                if ppu not in equipos:
                    equipos[ppu] = {
                        "marca": marca,
                        "modelo": modelo,
                        "prox_mant": prox_mant,
                        "horometros": {}
                    }
                equipos[ppu]["horometros"][fecha] = horometro

            # Estructurar datos para tabla
            registros = []
            for ppu, info in equipos.items():
                prox_mant = info["prox_mant"]
                ultimo_horo = ultimos.get(ppu)
                alerta = False

                if prox_mant and ultimo_horo:
                    if prox_mant - ultimo_horo <= 50:
                        alerta = True

                registros.append({
                    "ppu": ppu,
                    "marca": info["marca"],
                    "modelo": info["modelo"],
                    "prox_mant": prox_mant if prox_mant else "-",
                    "alerta": alerta,
                    "valores": [info["horometros"].get(f, "") for f in fechas],
                })

        except Exception as e:
            return render(request, "dashboard.html", {"mensaje": f"❌ Error procesando: {e}"})

    context = {
        "fechas": fechas,
        "registros": registros,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return render(request, "dashboard.html", context)

"""
DOMINIO = "https://api-equipos-ljq4.onrender.com/codigo/"

def generar_qr(request):
    mensaje = ""
    if request.method == "POST":
        # Procesar código único
        codigo = request.POST.get("codigo", "").upper()
        if len(codigo) != 7:
            mensaje = "El código debe tener 7 caracteres"
        else:
            url = f"{DOMINIO}{codigo}"
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")

            # Guardar en memoria y luego en modelo
            buffer = BytesIO()
            img.save(buffer, "PNG")
            buffer.seek(0)

            # Guardar en modelo
            qr_obj, created = QRCode.objects.get_or_create(codigo=codigo)
            qr_obj.qr_image.save(f"{codigo}.png", buffer, save=True)
            mensaje = f"QR generado para {url}"

        # Procesar Excel
        if 'excel' in request.FILES:
            archivo = request.FILES['excel']
            wb = openpyxl.load_workbook(archivo)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                codigo_excel = str(row[0]).upper()
                if len(codigo_excel) == 7:
                    url_excel = f"{DOMINIO}{codigo_excel}"
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(url_excel)
                    qr.make(fit=True)
                    img = qr.make_image(fill="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, "PNG")
                    buffer.seek(0)
                    qr_obj, created = QRCode.objects.get_or_create(codigo=codigo_excel)
                    qr_obj.qr_image.save(f"{codigo_excel}.png", buffer, save=True)
            mensaje += " | QR desde Excel generados"

    qr_list = QRCode.objects.all()
    return render(request, "generar_qr.html", {"mensaje": mensaje, "qr_list": qr_list})

    # return render(request, "generar_qr.html", {"mensaje": mensaje})
"""
