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
    """
    TODO: Docstring
    """
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
    """
    TODO: Docstring
    """
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        # TODO: Gestion de errores
        return False

    # Preparamos la estructura de la solicitud de compra
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        # TODO: Gestion de errores
        return False

    # Si el símbolo no está disponible en MarketWatch, lo añadimos
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            mt5.shutdown()
            # TODO: Gestion de errores
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
        "sl": stop_lose if stop_lose else price - 100 * point if action.lower() == "buy" else price + 100 * point,
        "tp": take_profit if take_profit else price + 100 * point if action.lower() == "buy" else price - 100 * point,
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
    """
    TODO: Docstring
    """
    return send_request_to_mt5(symbol, "BUY", lot, stop_lose, take_profit)


def sell(symbol, lot=None, stop_lose=None, take_profit=None):
    """
    TODO: Docstring
    """
    return send_request_to_mt5(symbol, "SELL", lot, stop_lose, take_profit)


def get_balance():
    """
    TODO: Docstring
    """
    raise NotImplementedError


# Primer ejemplo de algoritmo trading, usando 2 medias moviles (ver apuntes)
def moving_average_golden_dead_cross(data, symbol, short_window_size, long_window_size, time_trading_in_hours):
    """
    TODO: Docstring
    """
    # Crear dos medias moviles con ventanas de short_window_size dias y long_window_size dias
    SMA_short = pd.DataFrame()
    SMA_long = pd.DataFrame()

    # Repetir time_trading_in_hour horas nuestro algoritmo
    hours = 0
    while hours < time_trading_in_hours:
        hours += 1

        # Expando los datos hasta ahora mismo para ver en tiempo real
        df = common.update_data_to_realtime(data, symbol)

        # Ventana multiplicado por 24 ya que los datos son por hora y no por dia
        # O no multiplico para ventanas por horas
        SMA_short['time'] = df['time']
        SMA_long['time'] = df['time']
        SMA_short['ask'] = df['ask'].rolling(window=short_window_size).mean()
        SMA_long['ask'] = df['ask'].rolling(window=long_window_size).mean()

        # Visualizar datos del simbolo en hasta ahora y de 5 dias atras
        data_to_show = df[(df["time"] >= datetime.datetime.now() - datetime.timedelta(days=1)) & (
                df["time"] < datetime.datetime.now())]
        short_window = SMA_short[(SMA_short["time"] >= datetime.datetime.now() - datetime.timedelta(days=1)) & (
                df["time"] < datetime.datetime.now())]
        long_window = SMA_long[(SMA_long["time"] >= datetime.datetime.now() - datetime.timedelta(days=1)) & (
                df["time"] < datetime.datetime.now())]

        print(data_to_show)

        plt.figure(figsize=(16.5, 8.5))
        plt.plot(data_to_show['time'], data_to_show["ask"], label="ask")
        plt.plot(short_window['time'], short_window["ask"], label="Short moving average")
        plt.plot(long_window['time'], long_window["ask"], label="Long moving average")
        plt.title("EUR vs USD en el año 2020")
        plt.xlabel("Unidad de tiempo")
        plt.ylabel("Precio")
        plt.legend(loc="upper left")
        plt.show()

        # Cuando la MA a corto plazo supera a la de largo plazo → señal de compra (golden cross)
        # Cuando la MA a largo plazo supera a la de corto plazo → señal de venta (dead/death cross)

        # Esperar una hora hasta la siguiente actualizacion de precios
        time.sleep(3600.0)


if __name__ == '__main__':
    # Recogida de datos de cada simbolo a tratar
    symbols_names = ['EURUSD', 'XAUUSD', 'XAGEUR', 'XNGUSD', 'XBRUSD']
    dataframes = [common.get_data(symbol) for symbol in symbols_names]

    # Ejemplo moving average crossover
    moving_average_golden_dead_cross(dataframes[0], symbols_names[0], 3, 6, 8)
