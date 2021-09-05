import datetime
import warnings

from django.shortcuts import render, get_object_or_404

from .backend import common, utils, login, get_data_10_years
from .models import AlgoritmoTrading, Sesion, Mercado
from .strategies import moving_average, metodo_wyckoff

context = {}

warnings.simplefilter("ignore", category=RuntimeWarning)


# Funciones auxiliares

def add_sesion_to_context(request):
    context['sesion'] = \
        get_object_or_404(Sesion, user=request.user) \
            if request.user.username and request.user.username != 'admin' else None


def clear_context_status():
    context['error'] = None
    context['exito'] = None


def clear_context_ver_grafico():
    context['flag'] = 0
    context['mercado'] = None
    context['fecha_inicio'] = None
    context['fecha_fin'] = None
    context['horas'] = 0
    context['grafico'] = None
    context['marco_tiempo'] = None


# Vistas

def menu_principal(request):
    add_sesion_to_context(request)
    clear_context_status()
    if request.method == "POST":
        account = 0
        try:
            account = int(request.POST["account"])
        except ValueError:
            pass
        password = request.POST["password"]
        servidor = request.POST["servidor"]
        salida = login.login_mt5(account=account, password=password, servidor=servidor, sesion_actual=context['sesion'])
        if salida[0] == 1:
            context['error'] = salida[1]
        if salida[0] == 0:
            context['exito'] = salida[1]
    return render(request, "TradingAPP/menu_principal.html", context)


def menu_login(request):
    add_sesion_to_context(request)
    clear_context_status()
    return render(request, "TradingAPP/menu_login.html", context)


def menu_principal_logout(request):
    add_sesion_to_context(request)
    clear_context_status()
    login.logout_mt5(sesion_actual=context['sesion'])
    return render(request, "TradingAPP/menu_principal.html", context)


def ver_datos_mercados(request):
    add_sesion_to_context(request)
    clear_context_status()
    return render(request, "TradingAPP/ver_datos_mercados.html", context)


def ver_datos_antiguos(request):
    add_sesion_to_context(request)
    # Si no estoy actualizando el grafico con los botones tras haber entrado aqui, limpio el contexto
    if 'actualizar_grafico' not in request.POST:
        clear_context_ver_grafico()

    if request.method == "POST":
        # Cojo las variables de la requests
        context['mercado'] = context['sesion'].datos_mercado

        if not context.get('fecha_inicio'):
            fecha_inicio = request.POST["fecha_inicio"]
            context['fecha_inicio'] = fecha_inicio

        if not context.get('fecha_fin'):
            fecha_fin = request.POST["fecha_fin"]
            context['fecha_fin'] = fecha_fin

        # Cojo el objeto de la clase Mercado
        mercado = get_object_or_404(Mercado, pk=Mercado.objects.get(nombre=context.get('mercado')).id)

        marco_tiempo = context['sesion'].marco_tiempo

        # Actualizar el contador de ticks
        if 'actualizar_grafico' in request.POST:
            horas_totales = (utils.transform_date(context['fecha_fin']) -
                            utils.transform_date(context['fecha_inicio'])).total_seconds() // 3600
            velas_totales = horas_totales // int(marco_tiempo.replace('H', '')) if 'H' in marco_tiempo else \
                horas_totales // (int(marco_tiempo.replace('D', '')) * 24) if 'D' in marco_tiempo else \
                int(horas_totales / (int(marco_tiempo.replace('Min', '')) / 60)) if 'Min' in marco_tiempo else 1

            valor_flag = int(request.POST.get('actualizar_grafico', 0))

            if 0 <= context['flag'] + valor_flag <= velas_totales - 24:
                context['flag'] = context['flag'] + valor_flag

        # Genero el gráfico
        context["grafico"], context["exito"] = mercado.obtener_grafico_datos_antiguos(start=context.get('fecha_inicio'),
                                                                                      end=context.get('fecha_fin'),
                                                                                      flag=context.get('flag', 0),
                                                                                      marco_tiempo=
                                                                                      context.get('sesion').
                                                                                      marco_tiempo,
                                                                                      data=
                                                                                      context.get('sesion').raw_data)

    return render(request, "TradingAPP/ver_datos_antiguos.html", context)


def ver_datos_tiempo_real(request):
    add_sesion_to_context(request)
    clear_context_ver_grafico()
    if request.method == 'POST':
        # Cojo las variables de la requests
        nombre_mercado = 'EURUSD'  # Por defecto EURUSD por si hay algun error
        if not context.get('mercado'):
            nombre_mercado = request.POST["mercado"]
            context['mercado'] = nombre_mercado

        marco_tiempo = '1H'  # Por defecto 1H por si hay algun error
        if not context.get('marco_tiempo'):
            marco_tiempo = request.POST["marco_tiempo"]
            context['marco_tiempo'] = marco_tiempo

        # Cojo el objeto de la clase Mercado
        mercado = get_object_or_404(Mercado, pk=Mercado.objects.get(nombre=nombre_mercado).id)

        # Genero el gráfico
        context["grafico"], context["exito"] = mercado.obtener_grafico_datos_tiempo_real(marco_tiempo=marco_tiempo)

    return render(request, "TradingAPP/ver_datos_tiempo_real.html", context)


def estrategias_trading(request):
    add_sesion_to_context(request)
    clear_context_status()
    algoritmos = AlgoritmoTrading.objects.all()
    context.update({'algoritmos': algoritmos})
    return render(request, "TradingAPP/estrategias_trading.html", context)


def estrategias_trading_descripcion(request, algoritmo_id):
    add_sesion_to_context(request)
    clear_context_status()
    algoritmo = AlgoritmoTrading.objects.get(id=algoritmo_id)
    alg = {'id': algoritmo_id, 'nombre': algoritmo.nombre, 'descripcion': algoritmo.descripcion,
           'autor': algoritmo.autor, 'imagen': algoritmo.imagen}
    context.update({'algoritmo': alg})
    return render(request, "TradingAPP/estrategias_trading_descripcion.html", context)


def elegir_estrategia(request, algoritmo_id):
    add_sesion_to_context(request)
    clear_context_status()
    if request.method == "POST":
        algoritmo = AlgoritmoTrading.objects.get(id=algoritmo_id)
        context['sesion'].algoritmo_elegido = algoritmo
        context['sesion'].save()

    return render(request, "TradingAPP/elegir_estrategia.html", context)


def trading_auto(request):
    add_sesion_to_context(request)
    clear_context_status()
    return render(request, "TradingAPP/trading_auto.html", context)


def operar_auto(request):
    add_sesion_to_context(request)
    clear_context_status()
    if request.method == "POST":
        # Cojo las variables de la requests
        nombre_mercado = 'EURUSD'  # Por defecto EURUSD por si hay algun error
        if not context.get('mercado'):
            nombre_mercado = request.POST["mercado"]
            context['mercado'] = nombre_mercado

        marco_tiempo = '1H'  # Por defecto 1H por si hay algun error
        if not context.get('marco_tiempo'):
            marco_tiempo = request.POST["marco_tiempo"]
            context['marco_tiempo'] = marco_tiempo

        horas = -1  # Por defecto -1 por si hay algun error
        if not context.get('horas'):
            horas = request.POST["horas"]
            context['horas'] = horas

        try:
            if context['error']:
                return render(request, 'TradingAPP/operar_auto.html', context)
        except KeyError:
            pass

        mercado = get_object_or_404(Mercado, pk=Mercado.objects.get(nombre=nombre_mercado).id)

        # Se operará las horas especificadas, en el marco de tiempo y mercado indicados

        acciones = []
        plots = []
        beneficios = 0.0

        if context['sesion'].algoritmo_elegido.id == 1:  # Medias moviles
            # TODO
            raise

        if context['sesion'].algoritmo_elegido.id == 2:  # Metodo Wyckoff
            # Recogida de datos del simbolo a tratar
            # en formato ohlc con columnas (USANDO MT5)

            acciones, plots = metodo_wyckoff.metodo_wyckoff_tiempo_real(mercado=mercado, time_trading_in_hours=horas,
                                                                        marco_tiempo=marco_tiempo)

        context['acciones'] = acciones if acciones else [
            'No se ha realizado ninguna operación en el tiempo transcurrido']
        context['plots'] = plots if plots else ['']
        context['balance'] = beneficios
        return render(request, 'TradingAPP/operar_auto.html', context)


def backtesting_auto(request):
    add_sesion_to_context(request)
    clear_context_status()
    return render(request, "TradingAPP/backtesting_auto.html", context)


def operar_backtesting(request):
    add_sesion_to_context(request)
    clear_context_status()
    if request.method == "POST":
        inicio = request.POST["fecha_inicio"]
        fecha_inicio_datetime = utils.transform_date(inicio)
        try:
            horas = int(request.POST["horas"])
        except ValueError:
            horas = -1

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
        plots = []
        beneficios = 0.0

        if context['sesion'].algoritmo_elegido.id == 1:  # Medias moviles
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

        if context['sesion'].algoritmo_elegido.id == 2:  # Metodo Wyckoff
            # Recogida de datos del simbolo a tratar
            # en formato ohlc con columnas
            # time  ask_open  ask_high  ask_low  ask_close  bid_open  bid_high  bid_low  bid_close
            data = common.get_data_ohlc(mercado)

            acciones, plots = metodo_wyckoff.metodo_wyckoff_backtesting(data, start_date=fecha_inicio_datetime,
                                                                        time_trading_in_hours=horas)

        context['acciones'] = acciones if acciones else [
            'No se ha realizado ninguna operación en el tiempo transcurrido']
        context['plots'] = plots if plots else ['']
        context['balance'] = beneficios
        return render(request, 'TradingAPP/operar_backtesting.html', context)


def gestion_datos(request):
    add_sesion_to_context(request)
    clear_context_status()
    return render(request, "TradingAPP/menu_gestion_datos.html", context)


def obtener_y_guardar_datos(request):
    add_sesion_to_context(request)
    clear_context_status()
    if request.method == "POST":
        if not context['sesion'].raw_data:
            if not context.get('fecha_inicio'):
                inicio = request.POST["fecha_inicio"]
                context['fecha_inicio'] = inicio

            if not context.get('mercado'):
                nombre_mercado = request.POST["mercado"]
                context['mercado'] = nombre_mercado

            if not context.get('marco_tiempo'):
                marco_tiempo = request.POST["marco_tiempo"]
                context['marco_tiempo'] = marco_tiempo

            # Tenemos nombre_mercado, marco_tiempo, año inicio, obtengo datos y los guardo
            csv_text = get_data_10_years.get_data_csv_ohlc(context['fecha_inicio'], context['mercado'],
                                                           context['marco_tiempo'])
            context['sesion'].raw_data = csv_text
            context['sesion'].datos_mercado = context['mercado']
            context['sesion'].datos_inicio = context['fecha_inicio']
            context['sesion'].marco_tiempo = context['marco_tiempo']
            context['sesion'].save()

        return render(request, 'TradingAPP/proceso_datos_exito.html', context)


def borrar_datos(request):
    add_sesion_to_context(request)
    clear_context_status()
    context['sesion'].raw_data = ''
    context['sesion'].datos_mercado = ''
    context['sesion'].datos_inicio = ''
    context['sesion'].marco_tiempo = ''
    context['sesion'].save()

    return render(request, 'TradingAPP/proceso_datos_exito.html', context)
