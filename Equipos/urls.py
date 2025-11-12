from django.urls import path
from . import views

urlpatterns = [
    path('home/<str:codigo>/', views.home, name='home'), # Muestra el formulario del horómetro para un equipo específico.
    path('registro-manual/', views.registro_manual, name='registro_manual'), # Ingeso manual de horómetro.
    path('dashboard/', views.dashboard, name='dashboard'), # Muestra el "Dashboard" de datos ingresados en la BD.
]