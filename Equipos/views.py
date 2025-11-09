from django.shortcuts import render
from django.http import HttpResponse

def home(request, codigo):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        horometro = request.POST.get('horometro')
        
        # Aquí podrías guardar los datos en la base de datos si quisieras
        # Ejemplo:
        # RegistroHorometro.objects.create(codigo=codigo, rut=rut, horometro=horometro)

        return HttpResponse(f"Registro recibido para el equipo {codigo}: RUT {rut}, Horómetro {horometro}")

    # Si es GET, simplemente muestra el formulario con el código
    return render(request, 'equipos/home.html', {'codigo': codigo})
