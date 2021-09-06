# Funciones:
# Entrada -> datos, periodo para operar y mi cartera
# Salida -> historico de movimientos durante

import MetaTrader5 as mt5


def send_request_to_mt5(symbol, action, lot, stop_lose, take_profit):
    if not mt5.initialize():
        mt5.shutdown()
        return False

    # Preparamos la estructura de la solicitud de compra
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        mt5.shutdown()
        return False

    # Si el símbolo no está disponible en MarketWatch, lo añadimos
    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            mt5.shutdown()
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
        "sl": stop_lose,
        "tp": take_profit,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Mando la petición a MetaTrader
    order_result = mt5.order_send(request)

    return order_result


def buy(symbol, lot=None, sl=None, tp=None):
    return send_request_to_mt5(symbol, "BUY", lot=lot, take_profit=tp, stop_lose=sl)


def sell(symbol, lot=None, sl=None, tp=None):
    return send_request_to_mt5(symbol, "SELL", lot=lot, take_profit=tp, stop_lose=sl)
