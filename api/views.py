from django.shortcuts import render

def home(request, codigo=None):
    context = {'codigo': codigo}
    return render(request, 'home.html', context)