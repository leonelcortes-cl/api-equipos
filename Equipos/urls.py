from django.urls import path
from . import views

urlpatterns = [
    path('api/equipos/<str:codigo>/', views.buscar_equipo, name='buscar_equipo'),
]
