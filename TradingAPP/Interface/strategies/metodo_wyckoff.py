import datetime
from time import sleep

from ..backend import common
from ..backend.WyckoffTrading import WyckoffTradingBacktesting
from ..backend.operate import buy, sell


def metodo_wyckoff_backtesting(data, start_date=None, horas_totales=None, multiplicador=None,
                               imprimir_plot_por_hora=False, marco_tiempo=None):
    """
    TODO: Docstring
    """
    # Inicializo clase para parametros de Trading
    WTB = WyckoffTradingBacktesting()

    multiplicador = int(marco_tiempo.replace('H', '')) if 'H' in marco_tiempo else \
        int(marco_tiempo.replace('D', '')) * 24 if 'D' in marco_tiempo else \
            int(marco_tiempo.replace('Min', '')) / 60 if 'Min' in marco_tiempo else 1

    velas_totales = horas_totales // multiplicador

    # Repetir ticks_trading horas nuestro algoritmo
    velas = 0
    while velas < velas_totales:
        # Adapto los datos para no coger toda la data
        # df tendra los datos desde que tenemos datos (2011, por ejemplo), hasta start_date,
        # que es la fecha en la que empezaríamos a operar + horas que llevamos
        df = common.adapt_data_to_backtesting(data, start_date + datetime.timedelta(hours=velas * multiplicador + WTB.flag))

        if (start_date + datetime.timedelta(hours=velas * multiplicador + WTB.flag)).weekday() >= 5:
            # Actualizo la cuenta de horas de fines de semana
            WTB.flag += 48
        df = df[df.time.dt.weekday < 5]  # Elimino fines de semana

        # Cojo datos de la ultima semana para ver tendencias
        try:
            df_ultimas_30_velas = df.tail(24 * 7)
        except KeyError:
            df_ultimas_30_velas = df

        if not df_ultimas_30_velas.ask_close.iat[-1]:
            continue

        WTB.dataframe = df_ultimas_30_velas
        WTB.inicializar_valor_actual()

        # SI NO TENGO NINGUNA OPERACION EN CURSO, EMPIEZO ANALISIS
        if WTB.accion_actual == 0:
            # NUEVE TESTS DE COMPRA/VENTA DE WYCKOFF para una acumulación/distribución

            # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
            # vemos la ultima tendencia
            if not WTB.objetivo_cumplido:
                intervalos = WTB.comprobar_objetivo_cumplido()
                horas_hasta_completo = velas * multiplicador

            # El objetivo se ha cumplido, vemos si el intervalo del que venimos es alcista o bajista
            if WTB.objetivo_cumplido and not WTB.tendencia:
                print(WTB.intervalo)
                WTB.tendencia = common.BAJISTA if WTB.dataframe.loc[WTB.intervalo[0], 'ask_close'] - \
                                                  WTB.dataframe.loc[WTB.intervalo[-1], 'ask_close'] > 0 \
                    else common.ALCISTA

            # Si la tendencia ha sido bajista, 9 test de compra en una acumulación
            if WTB.tendencia == common.BAJISTA:
                WTB.test_compra_wyckoff()
                if WTB.accion_actual == 1:
                    horas_hasta_operacion = velas * multiplicador

            if WTB.tendencia == common.ALCISTA:
                WTB.test_venta_wyckoff()
                if WTB.accion_actual == 2:
                    horas_hasta_operacion = velas * multiplicador

        # DIBUJAR EL PLOT POR HORA, SOLO PARA DEBUG
        # SEA CUAL SEA LA ACCION O SI ESTOY EN FASE DE ANALISIS O NO
        # if imprimir_plot_por_hora:
        #     WTB.generar_dataframe(intervalos, horas_hasta_completo, hours)

        # Imprimo resultados de compra o venta
        if WTB.accion_actual == 1:
            if WTB.valor_actual <= WTB.stop_lose:
                print("ORDEN FALLIDA, HEMOS LLEGADO AL STOP LOSE")
                WTB.generar_dataframe(intervalos, horas_hasta_completo, velas * multiplicador,
                                      horas_hasta_operacion=horas_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['FALLIDA'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)
            elif WTB.valor_actual >= WTB.take_profit:
                print("ORDEN ACERTADA, HEMOS LLEGADO AL TAKE PROFIT")
                WTB.generar_dataframe(intervalos, horas_hasta_completo, velas * multiplicador,
                                      horas_hasta_operacion=horas_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['ACIERTO'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)

        if WTB.accion_actual == 2:
            if WTB.valor_actual >= WTB.stop_lose:
                print("ORDEN FALLIDA, HEMOS LLEGADO AL STOP LOSE")
                WTB.generar_dataframe(intervalos, horas_hasta_completo, velas * multiplicador,
                                      horas_hasta_operacion=horas_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['FALLIDA'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)
            elif WTB.valor_actual <= WTB.take_profit:
                print("ORDEN ACERTADA, HEMOS LLEGADO AL TAKE PROFIT")
                WTB.generar_dataframe(intervalos, horas_hasta_completo, velas * multiplicador,
                                      horas_hasta_operacion=horas_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['ACIERTO'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)

        # Simulo que pasa una hora (estoy en backtesting)
        velas += 1

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return WTB.acciones, WTB.plots


def metodo_wyckoff_tiempo_real(mercado, time_trading_in_hours=None, marco_tiempo=None):
    """
    TODO: Docstring
    """
    # Inicializo clase para parametros de Trading
    WTB = WyckoffTradingBacktesting()

    # Repetir time_trading_in_hours horas nuestro algoritmo
    # En cada iteracion, debemos de actualizar los datos, ya que estamos en tiempo real
    # Cada actualización se hara dependiendo del timeframe
    # Ejemplos:
    # 1min -> sleeps de 60 s
    # 1H -> sleeps de 3600 s

    to_sleep = int(marco_tiempo.replace('H', '')) * 3600 if 'H' in marco_tiempo else \
        int(marco_tiempo.replace('D', '')) * 24 * 3600 if 'D' in marco_tiempo else \
            int(marco_tiempo.replace('Min', '')) * 60 if 'Min' in marco_tiempo else 3600
    # En otro caso, lo dejo en 1 hora, que es lo que hay por defecto

    # El numero de iteraciones será las horas en segundos, entre los rangos
    # si damos 30 horas, en 1H, to_sleep sera 3600 -> iteraciones=30
    # si damos 1 hora, en 1Min, to_sleep sera 60 -> iteraciones=60
    iteraciones = int(time_trading_in_hours) * 3600 // to_sleep
    it = 0
    while it < iteraciones:
        print(it, iteraciones)
        # data ya estará preprocesado: ohlc, time como columna, sin fines de semana, etc.
        data = mercado.obtener_datos_tiempo_real(marco_tiempo=marco_tiempo)

        # En horas cogeriamos datos de la ultima semana para ver tendencias
        # En timeframe generico, cogemos ultimas 24*7 velas
        WTB.dataframe = data.tail(24 * 7)
        WTB.inicializar_valor_actual()

        # SI NO TENGO NINGUNA OPERACION EN CURSO, EMPIEZO ANALISIS
        if WTB.accion_actual == 0:
            # NUEVE TESTS DE COMPRA/VENTA DE WYCKOFF para una acumulación/distribución

            # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
            # vemos la ultima tendencia
            if not WTB.objetivo_cumplido:
                intervalos = WTB.comprobar_objetivo_cumplido()
                iteraciones_hasta_completo = it

            # El objetivo se ha cumplido, vemos si el intervalo del que venimos es alcista o bajista
            if WTB.objetivo_cumplido and not WTB.tendencia:
                WTB.tendencia = common.BAJISTA if WTB.dataframe.loc[WTB.intervalo[0], 'ask_close'] - \
                                                  WTB.dataframe.loc[WTB.intervalo[-1], 'ask_close'] > 0 \
                    else common.ALCISTA

            # Si la tendencia ha sido bajista, 9 test de compra en una acumulación
            if WTB.tendencia == common.BAJISTA:
                WTB.test_compra_wyckoff()
                if WTB.accion_actual == 1:
                    buy(mercado.nombre, sl=WTB.stop_lose, tp=WTB.take_profit)
                    iteraciones_hasta_operacion = it

            if WTB.tendencia == common.ALCISTA:
                WTB.test_venta_wyckoff()
                if WTB.accion_actual == 2:
                    sell(mercado.nombre, sl=WTB.stop_lose, tp=WTB.take_profit)
                    iteraciones_hasta_operacion = it

        # Imprimo resultados de compra o venta
        if WTB.accion_actual == 1:
            if WTB.valor_actual <= WTB.stop_lose:
                print("ORDEN FALLIDA, HEMOS LLEGADO AL STOP LOSE")
                WTB.generar_dataframe(intervalos, iteraciones_hasta_completo, it,
                                      horas_hasta_operacion=iteraciones_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['FALLIDA'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)
            elif WTB.valor_actual >= WTB.take_profit:
                print("ORDEN ACERTADA, HEMOS LLEGADO AL TAKE PROFIT")
                WTB.generar_dataframe(intervalos, iteraciones_hasta_completo, it,
                                      horas_hasta_operacion=iteraciones_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['ACIERTO'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)

        if WTB.accion_actual == 2:
            if WTB.valor_actual >= WTB.stop_lose:
                print("ORDEN FALLIDA, HEMOS LLEGADO AL STOP LOSE")
                WTB.generar_dataframe(intervalos, iteraciones_hasta_completo, it,
                                      horas_hasta_operacion=iteraciones_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['FALLIDA'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)
            elif WTB.valor_actual <= WTB.take_profit:
                print("ORDEN ACERTADA, HEMOS LLEGADO AL TAKE PROFIT")
                WTB.generar_dataframe(intervalos, iteraciones_hasta_completo, it,
                                      horas_hasta_operacion=iteraciones_hasta_operacion)
                WTB.acciones[len(WTB.acciones) - 1].extend(['ACIERTO'])
                WTB.reiniciar_analisis(WTB.acciones, WTB.plots, WTB.flag)

        # Simulo que pasa una hora (estoy en backtesting)
        it += 1
        print(f"Esperando {to_sleep} segundos ...")
        print(WTB.acciones)
        sleep(to_sleep)

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return WTB.acciones, WTB.plots
