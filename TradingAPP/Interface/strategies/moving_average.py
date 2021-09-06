# Primer ejemplo de algoritmo trading, usando 2 medias moviles (ver apuntes)
import datetime
import time

# import matplotlib.pyplot as plt
import pandas as pd

from ..backend import common
from ..backend.operate import buy, sell


def moving_average(data, symbol, short_window_size, long_window_size, backtesting=False,
                   backtesting_start_date=None, time_trading_in_hours=None):
    # Variable inicial para controlar si estoy comprando o vendiendo
    current_order = 0  # 0 = nada, 1 = buy, 2 = sell
    # Variable a devolver, con accion, precio y tiempo al que la hicimos
    acciones = []

    # Repetir time_trading_in_hours horas nuestro algoritmo
    hours = 0
    data_to_show = pd.DataFrame()
    while hours < time_trading_in_hours:
        # Crear dos medias moviles con ventanas de short_window_size dias y long_window_size dias
        SMA_short = pd.DataFrame()
        SMA_long = pd.DataFrame()

        # Expando los datos hasta ahora mismo para ver en tiempo real o backtesting
        df = common.update_data_to_realtime(data, symbol) if not backtesting \
            else common.adapt_data_to_backtesting(data, backtesting_start_date + datetime.timedelta(hours=hours))

        # Ventana multiplicado por 24 ya que los datos son por hora y no por dia
        # O no multiplico para ventanas por horas
        SMA_short['time'] = df['time']
        SMA_long['time'] = df['time']
        SMA_short['ask'] = df['ask'].rolling(window=short_window_size).mean()
        SMA_long['ask'] = df['ask'].rolling(window=long_window_size).mean()

        # Visualizar datos del simbolo hasta que tenemos datos y 1 dia atras (variara segun backtesting o realtime)
        date_until = datetime.datetime.now() if not backtesting else backtesting_start_date + datetime.timedelta(
            hours=hours)
        data_to_show = df[(df["time"] >= date_until - datetime.timedelta(days=1)) & (
                df["time"] < date_until)]

        short_window = SMA_short[(SMA_short["time"] >= date_until - datetime.timedelta(days=1)) & (
                df["time"] < date_until)]
        long_window = SMA_long[(SMA_long["time"] >= date_until - datetime.timedelta(days=1)) & (
                df["time"] < date_until)]
        #
        # plt.figure(figsize=(16.5, 8.5))
        # plt.plot(data_to_show['time'], data_to_show["ask"], label="ask")
        # plt.plot(short_window['time'], short_window["ask"], label="Short moving average")
        # plt.plot(long_window['time'], long_window["ask"], label="Long moving average")
        # plt.title("Precio y medias moviles por horas")
        # plt.xlabel("Unidad de tiempo")
        # plt.ylabel("Precio")
        # plt.legend(loc="upper left")
        # plt.show()

        # Cuando la MA a corto plazo supera a la de largo plazo → señal de compra (golden cross)
        # Cuando la MA a largo plazo supera a la de corto plazo → señal de venta (dead/death cross)
        # Creo variables y procedimiento:

        current_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']
        short_average_price = short_window.loc[short_window['time'].idxmax()]['ask']
        long_average_price = long_window.loc[long_window['time'].idxmax()]['ask']

        last_time = data_to_show['time'].max()

        if current_order == 0:  # sin accion
            if short_average_price > long_average_price:
                # MA corta > MA larga, comprar
                current_order = 1
                if not backtesting:
                    buy(symbol)
                acciones.append(['buy', last_time, current_price])
            elif long_average_price < short_average_price:
                # MA larga > MA corta, vender
                current_order = 2
                if not backtesting:
                    sell(symbol)
                acciones.append(['sell', last_time, current_price])

        elif current_order == 1:  # comprando
            if long_average_price > short_average_price:
                # MA larga > MA corta, vender
                # Cierro antes la operacion de compra
                current_order = 2
                if not backtesting:
                    sell(symbol)
                acciones.append(['sell', last_time, current_price])

        elif current_order == 2:  # vendiendo
            if short_average_price > long_average_price:
                # MA corta > MA larga, comprar
                # Cierro antes operacion de venta
                current_order = 1
                if not backtesting:
                    buy(symbol)
                acciones.append(['buy', last_time, current_price])

        hours += 1
        if not backtesting:
            # Esperar una hora hasta la siguiente actualizacion de precios
            time.sleep(3600.0)
        else:
            # Simulo que pasa una hora (estoy en backtesting)
            time.sleep(0.0)

    last_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return acciones, last_price
