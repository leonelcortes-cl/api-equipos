from django.urls import path
from . import views

urlpatterns = [
    # Muestra el formulario del horómetro para un equipo específico
    path('equipo/<str:codigo>/', views.home, name='home'),
]