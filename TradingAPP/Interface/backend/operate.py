# Funciones:
# Entrada -> datos, periodo para operar y mi cartera
# Salida -> historico de movimientos durante

import datetime

import MetaTrader5 as mt5
import matplotlib.pyplot as plt

plt.style.use("fivethirtyeight")


def send_request_to_mt5(symbol, action, lot=None):
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


def buy(symbol, lot=None):
    """
    TODO: Docstring
    """
    return send_request_to_mt5(symbol, "BUY", lot)


def sell(symbol, lot=None):
    """
    TODO: Docstring
    """
    return send_request_to_mt5(symbol, "SELL", lot)
