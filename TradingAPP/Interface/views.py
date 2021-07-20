import datetime
import warnings

from django.shortcuts import render, get_object_or_404

from .backend import common, utils
from .models import AlgoritmoTrading, Sesion, Mercado
from .strategies import moving_average, metodo_wyckoff

sesion_actual = Sesion.objects.all()[0]
context = {'sesion_actual': sesion_actual}

warnings.simplefilter("ignore", category=RuntimeWarning)


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
        fecha_inicio_datetime = utils.transform_date(inicio)
        horas = int(request.POST["horas"])

        # Compruebo que el número de horas es válido y que la fecha no cae en fin de semana y
        # no sale del rango de datos disponible
        if horas <= 0:
            context['error'] = 'ERROR: selecciona un número de horas válido'

        if fecha_inicio_datetime + datetime.timedelta(hours=horas) >= datetime.datetime(2021, 6, 22, 20):
            context['error'] = 'ERROR: selecciona un rango (fecha inicio + horas) dentro de los datos disponibles'

        if fecha_inicio_datetime.weekday() >= 5:
            context['error'] = 'ERROR: selecciona un día de inicio que sea sábado o domingo'

        try:
            if context['error']:
                return render(request, 'TradingAPP/operar_backtesting.html', context)
        except KeyError:
            pass

        nombre_mercado = request.POST["mercado"]
        mercado = get_object_or_404(Mercado, pk=Mercado.objects.get(nombre=nombre_mercado).id)

        # OPERAR BACKTESTING ENTRE INICIO Y FIN EN LA MONEDA mercado
        # ESTO SE DEBE ACTUALIZAR PARA COGER LOS DATOS QUE INSERTA EL USUARIO
        # Y GUARDAMOS EN BASE DE DATOS. AHORA MISMO COJO DATOS LOCALES

        acciones = []
        beneficios = 0.0

        if sesion_actual.algoritmo_elegido.id == 1:  # Medias moviles
            # Recogida de datos del simbolo a tratar
            data = common.get_data(mercado)

            ventana_pequena = int(request.POST["ventana_pequena"])
            ventana_grande = int(request.POST["ventana_grande"])

            # Moving average crossover
            # Parametrizar con las ventanas pequeña y grande que se quiera (3 y 6 por ej)
            # Ultimo parametro indica tiempo en horas que durará el trading

            acciones, ultimo_precio = \
                moving_average.moving_average(data, mercado, ventana_pequena, ventana_grande, backtesting=True,
                                              backtesting_start_date=fecha_inicio_datetime,
                                              time_trading_in_hours=horas)
            beneficios = common.get_actions_results(acciones, ultimo_precio)

        if sesion_actual.algoritmo_elegido.id == 2:  # Metodo Wyckoff
            # Recogida de datos del simbolo a tratar
            # en formato ohlc con columnas
            # time  ask_open  ask_high  ask_low  ask_close  bid_open  bid_high  bid_low  bid_close
            data = common.get_data_ohlc(mercado)

            acciones = metodo_wyckoff.metodo_wyckoff_backtesting(data, start_date=fecha_inicio_datetime,
                                                                 time_trading_in_hours=horas)

        context['acciones'] = acciones if acciones else [
            'No se ha realizado ninguna operación en el tiempo transcurrido']
        context['balance'] = beneficios
        return render(request, 'TradingAPP/operar_backtesting.html', context)
