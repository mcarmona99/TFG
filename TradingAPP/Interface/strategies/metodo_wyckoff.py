import datetime

import pandas as pd
import talib as ta

from ..backend import common


def metodo_wyckoff_backtesting(data, symbol, start_date=None, time_trading_in_hours=None):
    """
    TODO: Docstring
    """
    # Variable inicial para controlar si estoy comprando o vendiendo
    current_order = 0  # 0 = nada, 1 = buy, 2 = sell
    # Variable a devolver, con accion, precio y tiempo al que la hicimos
    acciones = []

    # Repetir time_trading_in_hours horas nuestro algoritmo
    hours = 0
    data_to_show = pd.DataFrame()
    while hours < time_trading_in_hours:
        # Adapto los datos para no coger toda la data
        # df tendra los datos desde que tenemos datos (2011, por ejemplo), hasta start_date,
        # que es la fecha en la que empezaríamos a operar + horas que llevamos
        df = common.adapt_data_to_backtesting(data, start_date + datetime.timedelta(hours=hours))
        df = df[df.time.dt.weekday < 5]  # Elimino fines de semana

        # Añado indicadores para ver tendencias
        df['SMA'] = ta.SMA(df.ask_close.values, 21)  # 21 periodos
        df['EMA'] = ta.EMA(df.ask_close.values, 55)  # 55 periodos de temporalidad

        # Bandas de Bollinger
        df['upper_band'], df['middle_band'], df['lower_band'] = ta.BBANDS(df['ask_close'], timeperiod=20)
        # idea para ver acumulaciones, distribuciones y tendencias con bollinger
        # columna diferencia de upper_band con lower_band, menores diferencias implican que el mercado está lateral
        # grandes diferencias arriba - abajo implica alcista
        # grandes diferencias abajo - arriba implica bajista
        # esto se puede ver si probamos a detectar anomalias en la columna pasada a numpy list

        # RSI
        df['RSI'] = ta.RSI(df.ask_close, 14)

        # Cojo datos de la ultima semana para ver tendencias
        df_ultimos_7_dias = df[start_date - datetime.timedelta(days=9) < df['time']]

        # Nueve tests de compra de Wyckoff para una acumulación
        # 1- El objetivo potencial bajista ya se ha cumplido – Gráfico de P&F

        # Simulo que pasa una hora (estoy en backtesting)
        hours += 1

    # last_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return acciones, 0
