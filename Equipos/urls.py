from django.urls import path
from . import views

urlpatterns = [
    #path('api/equipos/<str:codigo>/', views.buscar_equipo, name='buscar_equipo'),
    #path('api/equipos/<str:codigo>/', views.equipo_form, name='equipo_form'),
    path('', views.home, name='home'),
    path('api/equipos/<str:codigo>/', views.redirigir_a_home, name='redirigir'),
]
