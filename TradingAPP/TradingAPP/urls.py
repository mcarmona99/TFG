"""TradingAPP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from Interface import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Login principal
    path('accounts/', include('django.contrib.auth.urls')),

    # Menu principal
    path('', views.menu_principal, name='Menu Principal'),
    path('logout/', views.menu_principal_logout, name='Menu Principal Logout'),
    path('login/', views.menu_login, name='Menu Login'),

    # Urls de selección de estrategia
    path('estrategias/', views.estrategias_trading, name='Estrategias Trading'),
    path('estrategias/<int:algoritmo_id>/', views.estrategias_trading_descripcion, name='Elegir Estrategias Trading'),
    path('estrategias/<int:algoritmo_id>/elegir_estrategia_trading', views.elegir_estrategia),

    # Urls de operar
    path('trading/', views.trading_auto, name='Trading Automatico'),
    path('trading/operar_auto/', views.operar_auto, name='Operar Automatico'),

    # Urls de backtesting
    path('backtesting/', views.backtesting_auto, name='Backtesting Automatico'),
    path('backtesting/operar_backtesting/', views.operar_backtesting, name='Operar Backtesting'),

    # Urls de ver datos de mercados
    path('mercados/', views.ver_datos_mercados, name="Menu Ver Datos"),
    path('mercados/ver_datos_antiguos/', views.ver_datos_antiguos, name="Ver Datos Antiguos"),
    path('mercados/ver_datos_tiempo_real/', views.ver_datos_tiempo_real, name="Ver Datos Tiempo Real"),

    # Gestion de datos
    path('datos/', views.gestion_datos, name="Gestion Datos"),
    path('datos/obtener_datos/', views.obtener_y_guardar_datos, name="Datos obtenidos"),
    path('datos/borrar_datos/', views.borrar_datos, name="Borrar datos"),

    # Manual de uso
    path('manual_uso/', views.manual_uso, name="Manual uso"),

    # Admin page
    path('admin/', admin.site.urls),
]
