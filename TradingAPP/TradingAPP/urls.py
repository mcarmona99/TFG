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
from django.urls import path

urlpatterns = [
    # Menu principal
    path('', views.menu_principal, name='Menu Principal'),
    path('logout/', views.menu_principal_logout, name='Menu Principal Logout'),
    path('login/', views.menu_login, name='Menu Login'),

    # Urls de selección de estrategia
    path('estrategias/', views.estrategias_trading, name='Estrategias Trading'),
    path('estrategias/<int:algoritmo_id>/', views.estrategias_trading_descripcion, name='Elegir Estrategias Trading'),
    path('estrategias/<int:algoritmo_id>/elegir_estrategia_trading', views.elegir_estrategia),

    # Urls de backtesting
    path('backtesting/', views.menu_backtesting, name='Backtesting'),
    path('backtesting/automatico/', views.backtesting_auto, name='Backtesting Automatico'),
    path('backtesting/automatico/operar_backtesting/', views.operar_backtesting, name='Operar Backtesting'),

    # Urls de ver datos de mercados
    path('mercados/', views.ver_datos_mercados, name="Menu Ver Datos"),
    path('mercados/ver_datos_antiguos/', views.ver_datos_antiguos, name="Ver Datos Antiguos"),
]
