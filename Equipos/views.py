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

    if not equipo:
        # Si el equipo no existe
        return render(request, 'equipos/home.html', {
            'codigo': codigo,
            'existe': False
        })

    # Desempaquetar los valores de la tupla
    marca, modelo = equipo
    mensaje = None
    autorizado = None
    nombre = None
    apellidos = None

    # Si el usuario envía el formulario
    if request.method == "POST":
        rut = request.POST.get('rut')
        horometro = request.POST.get('horometro')

        # Validar el RUT en la tabla de operadores
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT dtTxt_Nombre, dtTxt_Apellidos
                FROM tdOperadores
                WHERE idNum_RUT = %s
            """, [rut])
            operador = cursor.fetchone()

        if operador:
            nombre, apellidos = operador
            autorizado = True
            mensaje = f"✅ Operador autorizado: {nombre} {apellidos}"
        else:
            autorizado = False
            mensaje = f"❌ RUT {rut} no está autorizado para operar este equipo."

    # Renderizar la vista con toda la información
    return render(request, 'equipos/home.html', {
        'codigo': codigo,
        'marca': marca,
        'modelo': modelo,
        'existe': True,
        'autorizado': autorizado,
        'mensaje': mensaje,
        'nombre': nombre,
        'apellidos': apellidos
    })