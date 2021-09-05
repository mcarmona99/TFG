# Primer script para una estrategia simple de trading
# Funciones:
# Entrada -> datos, periodo para operar y mi cartera
# Salida -> historico de movimientos durante

import datetime
import time

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd

import common

plt.style.use("fivethirtyeight")


def login():
    # if mt5.login(
    #     login,                 # número de cuenta
    #     password = "PASSWORD", # contraseña. No obligatorio.
    #                            # Si no se indica la contraseña, se utilizará automáticamente la contraseña guardada
    #                            # en la base de datos del terminal.
    #     server = "SERVER",     # nombre del servidor como se ha establecido en el terminal
    #     timeout = TIMEOUT      # timeout
    # ):
    # print(mt5.account_info())
    # return True
    raise NotImplementedError


def send_request_to_mt5(symbol, action, lot=None, stop_lose=None, take_profit=None):
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return False

    # Preparamos la estructura de la solicitud de compra
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        return False

    # Si el símbolo no está disponible en MarketWatch, lo añadimos
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            mt5.shutdown()
            return False

    # Creo variables y peticion request a mandar
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot if lot else 0.01,
        "type": mt5.ORDER_TYPE_BUY if action.lower() == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        # "sl": stop_lose if stop_lose else price - 100 * point if action.lower() == "buy" else price + 100 * point,
        # "tp": take_profit if take_profit else price + 100 * point if action.lower() == "buy" else price - 100 * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Mando la petición a MetaTrader
    order_result = mt5.order_send(request)

    return order_result


def buy(symbol, lot=None, stop_lose=None, take_profit=None):
    return send_request_to_mt5(symbol, "BUY", lot, stop_lose, take_profit)


def sell(symbol, lot=None, stop_lose=None, take_profit=None):
    return send_request_to_mt5(symbol, "SELL", lot, stop_lose, take_profit)


def get_balance():
    raise NotImplementedError


# Primer ejemplo de algoritmo trading, usando 2 medias moviles (ver apuntes)
def moving_average_golden_dead_cross(data, symbol, short_window_size, long_window_size, backtesting=False,
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

        plt.figure(figsize=(16.5, 8.5))
        plt.plot(data_to_show['time'], data_to_show["ask"], label="ask")
        plt.plot(short_window['time'], short_window["ask"], label="Short moving average")
        plt.plot(long_window['time'], long_window["ask"], label="Long moving average")
        plt.title("Precio y medias moviles por horas")
        plt.xlabel("Unidad de tiempo")
        plt.ylabel("Precio")
        plt.legend(loc="upper left")
        plt.show()

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

        print(f"\nAcciones hechas hasta ahora (llevo {hours} horas):")
        for accion in acciones:
            print(f"Accion: {accion[0]} | Fecha y hora: {accion[1]} | Precio: {accion[2]}")

        hours += 1
        if not backtesting:
            # Esperar una hora hasta la siguiente actualizacion de precios
            time.sleep(3600.0)
        else:
            # Simulo que pasa una hora (estoy en backtesting)
            time.sleep(0.0)

    last_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']
    print(f"\nULTIMO PRECIO: {last_price}")

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return acciones, last_price


if __name__ == '__main__':
    # Recogida de datos de cada simbolo a tratar
    symbols_names = ['EURUSD', 'XAUUSD', 'XAGEUR', 'XNGUSD', 'XBRUSD']
    dataframes = [common.get_data(symbol) for symbol in symbols_names]

    # Ejemplo moving average crossover
    # Parametrizar con las ventanas pequeña y grande que se quiera (3 y 6 por ej)
    # Ultimo parametro indica tiempo en horas que durará el trading

    acciones, ultimo_precio = moving_average_golden_dead_cross(dataframes[0], symbols_names[0], 5, 15, backtesting=True,
                                                               backtesting_start_date=datetime.datetime(2020, 10, 8),
                                                               time_trading_in_hours=48)
    beneficios = common.get_actions_results(acciones, ultimo_precio)

    print(f"\nLista con las acciones que he ido haciendo: {acciones}")
    print(f"\nBalance: {beneficios}")
