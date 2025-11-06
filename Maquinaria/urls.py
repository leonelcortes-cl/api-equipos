from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('Equipos.urls')),
    path('api/equipos/<str:codigo>/', views.home, name='home_con_codigo'),
    
]

