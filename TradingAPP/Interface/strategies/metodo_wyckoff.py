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

        # Bandas de Bollinger con media movil de 20 (middle_band)
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

        # Nueve tests de compra/venta de Wyckoff para una acumulación
        # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
        indicador_tendencia_bollinger = df['upper_band'].to_numpy() - df['lower_band']

        # Simulo que pasa una hora (estoy en backtesting)
        hours += 1

    # last_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']

    # Devuelvo el vector de acciones realizadas con su precio y datetime
    return acciones, 0



# SCRATCH HECHO

# import datetime
# import os
# import re
# import time
# import warnings
#
# import numpy as np
# import pandas as pd
# import talib as ta
# from matplotlib import pyplot as plt
# from pandas.core.common import SettingWithCopyWarning
#
# warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
#
# DATA_PATH_OHLC = os.path.abspath('/Users/masus/git/TFG/data')
#
# print(DATA_PATH_OHLC)
#
#
# def find_files_regex(filename, search_path):
#     """
#     TODO: Docstring
#     """
#     files_found = []
#     regex = re.compile('.*{}.*'.format(filename))
#     for root, dirs, files in os.walk(search_path):
#         for file in files:
#             if regex.match(file):
#                 files_found.append(os.path.join(root, file))
#
#     return files_found
#
#
# def get_data_ohlc(symbol, data_path=DATA_PATH_OHLC):
#     """
#     TODO: Docstring
#     """
#     frames = []
#     for file in find_files_regex(symbol, data_path):
#         df_file = pd.read_csv(file, header=2)
#
#         # Rename columns
#         df_file.columns = ['time',
#                            'ask_open', 'ask_high', 'ask_low', 'ask_close',
#                            'bid_open', 'bid_high', 'bid_low', 'bid_close']
#
#         df_file['time'] = pd.to_datetime(df_file['time'], dayfirst=False, yearfirst=True)
#
#         frames.append(df_file)
#
#     try:
#         df = pd.concat(frames)
#     except ValueError:
#         print(f"No se han encontrado dataframes para {symbol} en {data_path}")
#         # TODO: Gestion de errores
#         return None
#
#     return df
#
#
# def adapt_data_to_backtesting(old_dataframe, end_data):
#     """
#     TODO: Docstring
#     """
#     return old_dataframe[old_dataframe['time'] < end_data]
#
#
# def metodo_wyckoff_backtesting(data, symbol, start_date=None, time_trading_in_hours=None):
#     """
#     TODO: Docstring
#     """
#     # Variable inicial para controlar si estoy comprando o vendiendo
#     current_order = 0  # 0 = nada, 1 = buy, 2 = sell
#     # Variable a devolver, con accion, precio y tiempo al que la hicimos
#     acciones = []
#
#     # Repetir time_trading_in_hours horas nuestro algoritmo
#     hours = 0
#     while hours < time_trading_in_hours:
#         # Adapto los datos para no coger toda la data
#         # df tendra los datos desde que tenemos datos (2011, por ejemplo), hasta start_date,
#         # que es la fecha en la que empezaríamos a operar + horas que llevamos
#         df = adapt_data_to_backtesting(data, start_date + datetime.timedelta(hours=hours))
#         df = df[df.time.dt.weekday < 5]  # Elimino fines de semana
#
#         # Añado indicadores para ver tendencias
#         df['SMA'] = ta.SMA(df.ask_close.values, 21)  # 21 periodos
#         df['EMA'] = ta.EMA(df.ask_close.values, 55)  # 55 periodos de temporalidad
#
#         # Cojo datos de la ultima semana para ver tendencias
#         df_ultimos_7_dias = df[start_date - datetime.timedelta(days=9) + datetime.timedelta(hours=hours) < df['time']]
#
#         # Bandas de Bollinger con media movil de 20 (middle_band)
#         df_ultimos_7_dias['upper_band'], df_ultimos_7_dias['middle_band'], df_ultimos_7_dias['lower_band'] = \
#             ta.BBANDS(df_ultimos_7_dias['ask_close'], timeperiod=20)
#         # idea para ver acumulaciones, distribuciones y tendencias con bollinger
#         # columna diferencia de upper_band con lower_band, menores diferencias implican que el mercado está lateral
#         # grandes diferencias arriba - abajo implica alcista
#         # grandes diferencias abajo - arriba implica bajista
#         # esto se puede ver si probamos a detectar anomalias en la columna pasada a numpy list
#
#         # RSI
#         df_ultimos_7_dias['RSI'] = ta.RSI(df_ultimos_7_dias.ask_close, 14)
#
#         # df_ultimos_7_dias[['ask_close','upper_band','middle_band','lower_band']].plot()
#         # plt.show()
#
#         # Nueve tests de compra/venta de Wyckoff para una acumulación
#         # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
#         diferencia_bandas = df_ultimos_7_dias['upper_band'].to_numpy() - df_ultimos_7_dias['lower_band'].to_numpy()
#         diferencia_bandas = np.array(diferencia_bandas)
#
#         # DETECTO LAS ANOMALIAS DE LA DIFERENCIA DE LAS BANDAS, ESTO ME DARA INTERVALOS DE CRECIMIENTO Y DECRECIMIENTO
#         media_de_diferencias = np.mean(diferencia_bandas[~np.isnan(diferencia_bandas)])
#         anomalias = [i if not np.isnan(i) and i > media_de_diferencias else np.nan for i in diferencia_bandas]
#         indices_anomalias = [indice if not np.isnan(a) else np.nan for indice, a in enumerate(anomalias)]
#
#         intervalos = []
#         intervalo = []
#         for i in indices_anomalias:
#             if not np.isnan(i):
#                 intervalo.append(i)
#             else:
#                 if intervalo:
#                     intervalos.append(intervalo)
#                     intervalo = []
#
#         len_x = range(len(df_ultimos_7_dias))
#         plt.plot(len_x, df_ultimos_7_dias['ask_close'])
#         plt.plot(len_x, df_ultimos_7_dias['upper_band'])
#         plt.plot(len_x, df_ultimos_7_dias['lower_band'])
#         [plt.axvspan(i[0], i[-1], facecolor='b', alpha=0.5) for i in intervalos]
#         plt.show()
#
#         # Simulo que pasa una hora (estoy en backtesting)
#         hours += 1
#         time.sleep(1)
#
#     # last_price = data_to_show.loc[data_to_show['time'].idxmax()]['ask']
#
#     # Devuelvo el vector de acciones realizadas con su precio y datetime
#     return acciones, 0
#
#
# inicio = datetime.datetime(2019, 3, 21)
# horas = 64
# nombre_mercado = 'EURUSD'
#
# acciones = []
# beneficios = 0.0
#
# # Recogida de datos del simbolo a tratar
# # en formato ohlc con columnas
# # time  ask_open  ask_high  ask_low  ask_close  bid_open  bid_high  bid_low  bid_close
# data = get_data_ohlc(nombre_mercado)
#
# acciones, ultimo_precio = metodo_wyckoff_backtesting(data, nombre_mercado,
#                                                      start_date=inicio,
#                                                      time_trading_in_hours=int(horas))
# # beneficios = common.get_actions_results(acciones, ultimo_precio)
