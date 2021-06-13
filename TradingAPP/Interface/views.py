from django.shortcuts import render

from .models import AlgoritmoTrading, Sesion

sesion_actual = Sesion.objects.all()[0]


def menu_principal(request):
    context = {'sesion': sesion_actual}
    return render(request, "TradingAPP/menu_principal.html", context)


def estrategias_trading(request):
    algoritmos = AlgoritmoTrading.objects.all()
    context = {'algoritmos': algoritmos, 'sesion': sesion_actual}
    return render(request, "TradingAPP/estrategias_trading.html", context)


def estrategias_trading_elegir(request, algoritmo_id):
    algoritmo = AlgoritmoTrading.objects.get(id=algoritmo_id)
    alg = {'id': algoritmo_id, 'nombre': algoritmo.nombre, 'descripcion': algoritmo.descripcion,
           'autor': algoritmo.autor, 'imagen': algoritmo.imagen}
    context = {'algoritmo': alg, 'sesion': sesion_actual}
    return render(request, "TradingAPP/estrategias_trading_elegir.html", context)
