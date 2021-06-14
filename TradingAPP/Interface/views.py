from django.shortcuts import render, get_object_or_404

from .backend import common, utils
from .models import AlgoritmoTrading, Sesion, Mercado
from .strategies import moving_average

sesion_actual = Sesion.objects.all()[0]
context = {'sesion_actual': sesion_actual}


def menu_principal(request):
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

    return render(request, "TradingAPP/elegir_estrategia.html", context)


def menu_backtesting(request):
    return render(request, "TradingAPP/menu_backtesting.html", context)


def backtesting_auto(request):
    return render(request, "TradingAPP/backtesting_auto.html", context)


def operar_backtesting(request):
    if request.method == "POST":
        inicio = request.POST["fecha_inicio"]
        horas = request.POST["horas"]
        nombre_mercado = request.POST["mercado"]
        mercado = get_object_or_404(Mercado, pk=Mercado.objects.get(nombre=nombre_mercado).id)

        # OPERAR BACKTESTING ENTRE INICIO Y FIN EN LA MONEDA mercado
        # ESTO SE DEBE ACTUALIZAR PARA COGER LOS DATOS QUE INSERTA EL USUARIO
        # Y GUARDAMOS EN BASE DE DATOS. AHORA MISMO COJO DATOS LOCALES

        # Recogida de datos del simbolo a tratar
        data = common.get_data(mercado)
        acciones = []
        beneficios = 0.0

        if sesion_actual.algoritmo_elegido.nombre == 'Medias moviles':
            # Moving average crossover
            # Parametrizar con las ventanas pequeña y grande que se quiera (3 y 6 por ej)
            # Ultimo parametro indica tiempo en horas que durará el trading

            acciones, ultimo_precio = \
                moving_average.moving_average(data, mercado, 5, 15, backtesting=True,
                                              backtesting_start_date=utils.transform_date(inicio),
                                              time_trading_in_hours=int(horas))
            beneficios = common.get_actions_results(acciones, ultimo_precio)

        context['acciones'] = acciones
        context['balance'] = beneficios
        return render(request, 'TradingAPP/operar_backtesting.html', context)
