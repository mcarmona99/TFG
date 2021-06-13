from django.shortcuts import render

from .models import AlgoritmoTrading, Sesion

sesion_actual = Sesion.objects.all()[0]


def menu_principal(request):
    context = {'sesion_actual': sesion_actual}
    return render(request, "TradingAPP/menu_principal.html", context)


def estrategias_trading(request):
    algoritmos = AlgoritmoTrading.objects.all()
    context = {'algoritmos': algoritmos, 'sesion_actual': sesion_actual}
    return render(request, "TradingAPP/estrategias_trading.html", context)


def estrategias_trading_descripcion(request, algoritmo_id):
    algoritmo = AlgoritmoTrading.objects.get(id=algoritmo_id)
    alg = {'id': algoritmo_id, 'nombre': algoritmo.nombre, 'descripcion': algoritmo.descripcion,
           'autor': algoritmo.autor, 'imagen': algoritmo.imagen}
    context = {'algoritmo': alg, 'sesion_actual': sesion_actual}
    return render(request, "TradingAPP/estrategias_trading_descripcion.html", context)


def elegir_estrategia(request, algoritmo_id):
    if request.method == "POST":
        algoritmo = AlgoritmoTrading.objects.get(id=algoritmo_id)
        sesion_actual.algoritmo_elegido = algoritmo
        sesion_actual.save()

    context = {'sesion_actual': sesion_actual}
    return render(request, "TradingAPP/elegir_estrategia.html", context)
