from django.urls import path
from . import views

urlpatterns = [
    # Página principal del módulo de equipos
    path('', views.home, name='home'),

    # Detalle de un equipo por código
    path('equipo/<str:codigo>/', views.detalle_equipo, name='detalle_equipo'),
]
