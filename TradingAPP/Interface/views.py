from django.shortcuts import render

from .models import Sesion

sesion = Sesion.create(algoritmo_elegido=None)


def menu_principal(request):
    return render(request, "TradingAPP/menu_principal.html")


def estrategias_trading(request):
    algoritmo_elegido = sesion.algoritmo_elegido
    context = {'algoritmo_elegido': algoritmo_elegido}
    return render(request, "TradingAPP/estrategias_trading.html", context)
