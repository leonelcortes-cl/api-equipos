from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.utils import timezone
import mysql.connector
from django.conf import settings

def buscar_equipo(request, codigo):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tdEquipos WHERE idTxt_Ppu = %s", [codigo])
        resultado = cursor.fetchone()

    if resultado:
        return HttpResponse(f"✅ Equipo encontrado: {resultado}")
    else:
        return HttpResponse("❌ No existe ningún equipo con ese código.")



def equipo_form(request, codigo):
    if request.method == "POST":
        rut = request.POST.get("rut")
        horometro = request.POST.get("horometro")

        # Conexión directa a la BD
        conn = mysql.connector.connect(
            host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tdHorometros (
                idNum_Registro INT AUTO_INCREMENT PRIMARY KEY,
                dtTxt_Ppu VARCHAR(20),
                dtTxt_Rut VARCHAR(20),
                dtNum_Horometro DECIMAL(10,2),
                dtFec_Fecha DATETIME
            )
        """)

        # Insertar datos
        cursor.execute("""
            INSERT INTO tdHorometros (dtTxt_Ppu, dtTxt_Rut, dtNum_Horometro, dtFec_Fecha)
            VALUES (%s, %s, %s, %s)
        """, (codigo, rut, horometro, timezone.now()))

        conn.commit()
        conn.close()

        return HttpResponse("<h2>✅ Registro guardado correctamente</h2>")

    # Si es GET → muestra el formulario
    return render(request, "equipos_form.html", {"codigo": codigo})
