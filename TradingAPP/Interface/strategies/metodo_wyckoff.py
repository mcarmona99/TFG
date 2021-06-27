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
# BAJISTA = 'bajista'
# ALCISTA = 'alcista'
#
# print(DATA_PATH_OHLC)
#
#
# def get_actions_results(acciones, ultimo_precio):
#     comprando = False
#     if acciones[0][0] == 'buy':
#         comprando = True
#
#     beneficio = 0.0
#     for i in range(0, len(acciones) - 1):
#         beneficio = beneficio + acciones[i + 1][2] - acciones[i][2] if comprando \
#             else beneficio + acciones[i][2] - acciones[i + 1][2]
#         comprando = False if comprando else True
#
#     beneficio = beneficio + ultimo_precio - acciones[len(acciones) - 1][2] if comprando \
#         else beneficio + acciones[len(acciones) - 1][2] - ultimo_precio
#
#     return beneficio
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
# def comprobar_objetivo_cumplido(df_ultimos_7_dias):
#     # Obtenemos en tiempo real un objetivo cumplido, alcista o bajista
#
#     # Bandas de Bollinger con media movil de 20 (middle_band)
#     df_ultimos_7_dias['upper_band'], df_ultimos_7_dias['middle_band'], df_ultimos_7_dias['lower_band'] = \
#         ta.BBANDS(df_ultimos_7_dias['ask_close'], timeperiod=20)
#     # idea para ver acumulaciones, distribuciones y tendencias con bollinger
#     # columna diferencia de upper_band con lower_band, menores diferencias implican que el mercado está lateral
#     # grandes diferencias arriba - abajo implica alcista
#     # grandes diferencias abajo - arriba implica bajista
#     # esto se puede ver si probamos a detectar anomalias en la columna pasada a numpy list
#
#     diferencia_bandas = df_ultimos_7_dias['upper_band'].to_numpy() - df_ultimos_7_dias['lower_band'].to_numpy()
#     diferencia_bandas = np.array(diferencia_bandas)
#
#     # DETECTO LAS ANOMALIAS DE LA DIFERENCIA DE LAS BANDAS, ESTO ME DARA INTERVALOS DE CRECIMIENTO Y DECRECIMIENTO
#     media_de_diferencias = np.mean(diferencia_bandas[~np.isnan(diferencia_bandas)])
#     anomalias = [i if not np.isnan(i) and i > media_de_diferencias else np.nan for i in diferencia_bandas]
#     indices_anomalias = [indice if not np.isnan(a) else np.nan for indice, a in enumerate(anomalias)]
#
#     intervalos = []
#     intervalo = []
#     intervalos_indice_global = []
#     intervalo_i_global = []
#     for i in indices_anomalias:
#         if not np.isnan(i):
#             intervalo.append(i)
#             intervalo_i_global.append(df_ultimos_7_dias.index[i])
#         else:
#             if intervalo:
#                 intervalos.append(intervalo)
#                 intervalos_indice_global.append(intervalo_i_global)
#                 intervalo_i_global = []
#                 intervalo = []
#
#     # Tengo los intervalos de crecimiento y decrecimiento
#     objetivo_cumplido = False
#     for intervalo_i_global in intervalos_indice_global:
#         objetivo_cumplido = df_ultimos_7_dias.index[-2] in intervalo_i_global
#
#     return intervalos_indice_global[-1], objetivo_cumplido, intervalos
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
#     objetivo_cumplido = False
#     intervalo = []
#     tendencia = False
#     puntos_clave_calculados = False
#     media_calculada = False
#     tendencia_rota = False
#     indicadores_operar = 0.0
#     ultimo_maximo = 0.0
#     ultimo_minimo = 0.0
#     flag = 0
#     while hours < time_trading_in_hours:
#         # Adapto los datos para no coger toda la data
#         # df tendra los datos desde que tenemos datos (2011, por ejemplo), hasta start_date,
#         # que es la fecha en la que empezaríamos a operar + horas que llevamos
#         df = adapt_data_to_backtesting(data, start_date + datetime.timedelta(hours=hours+flag))
#         if (start_date + datetime.timedelta(hours=hours + flag)).weekday() >= 5:
#             flag += 48
#         df = df[df.time.dt.weekday < 5]  # Elimino fines de semana
#
#         # Cojo datos de la ultima semana para ver tendencias
#         df_ultimos_7_dias = df.tail(24 * 7)
#
#         # NUEVE TESTS DE COMPRA/VENTA DE WYCKOFF para una acumulación/distribución
#
#         # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
#         # vemos la ultima tendencia
#         if not objetivo_cumplido:
#             intervalo, objetivo_cumplido, intervalos = comprobar_objetivo_cumplido(df_ultimos_7_dias)
#             horas_hasta_completo = hours
#
#         # El objetivo se ha cumplido, vemos si el intervalo del que venimos es alcista o bajista
#         if objetivo_cumplido and not tendencia:
#             tendencia = BAJISTA if df_ultimos_7_dias.loc[intervalo[0], 'ask_close'] - \
#                                    df_ultimos_7_dias.loc[intervalo[-1], 'ask_close'] > 0 \
#                 else ALCISTA
#
#         # Si la tendencia ha sido bajista, 9 test de compra en una acumulación
#         if tendencia == BAJISTA:
#             valor_actual = df_ultimos_7_dias['ask_close'][df_ultimos_7_dias.index[-1]]
#             if not puntos_clave_calculados:
#                 # 1- El objetivo potencial bajista ya se ha cumplido
#                 indicadores_operar += 1
#                 print(f"+ Objetivo potencial bajista cumplido, indicadores cumplidos = {indicadores_operar}")
#
#                 # 2- PS, SC, AR y ST
#                 # SC: selling climax
#                 vector_sc = [valor for valor in [df_ultimos_7_dias.loc[i, 'ask_close'] for i in intervalo]]
#                 selling_climax = min(vector_sc)
#                 indice_sc = intervalo[vector_sc.index(selling_climax)]
#
#                 # AR: automatic rally, será el maximo obtenido despues del SC en lo que consideramos
#                 # la tendencia, que la hemos sacado con anomalias
#                 vector_ar = [valor for valor in
#                              [df_ultimos_7_dias.loc[i, 'ask_close'] for i in intervalo[intervalo.index(indice_sc):]]]
#                 automatic_rally = max(vector_ar)
#
#                 puntos_clave_calculados = True
#                 ultimo_minimo = selling_climax
#                 ultimo_maximo = automatic_rally
#
#             # 4- La tendencia bajista se ha roto
#             # (es decir, línea de oferta o línea de tendencia bajista ha sido rota)
#             # Implementado con media movil
#             df_ultimos_7_dias['SMA'] = ta.SMA(df_ultimos_7_dias.ask_close.values, 10)  # 21 periodos
#             media_calculada = True
#
#             if not tendencia_rota and valor_actual > df_ultimos_7_dias['SMA'][df_ultimos_7_dias.index[-1]]:
#                 # La tendencia bajista se ha roto
#                 indicadores_operar += 1
#                 print(f"+ Tendencia bajista se ha roto, indicadores cumplidos = {indicadores_operar}")
#                 tendencia_rota = True
#
#             # 5- Minimos mas altos
#             if valor_actual > ultimo_minimo and valor_actual < ultimo_maximo:
#                 indicadores_operar += 0.5
#                 print(f"+ Minimo mas alto, indicadores cumplidos = {indicadores_operar}")
#                 ultimo_minimo = valor_actual
#
#             # 6- Maximos mas altos
#             elif valor_actual > ultimo_maximo:
#                 indicadores_operar += 0.5
#                 print(f"+ Maximo mas alto, indicadores cumplidos = {indicadores_operar}")
#                 ultimo_maximo = valor_actual
#
#             # Minimos mas bajos, resto puntos
#             elif valor_actual < ultimo_minimo:
#                 indicadores_operar -= 0.5
#                 print(f"- Minimo mas bajo, indicadores cumplidos = {indicadores_operar}")
#                 ultimo_minimo = valor_actual
#
#
#             # Hemos pasado la linea superior de Bollinguer
#             df_ultimos_7_dias['upper_band'], df_ultimos_7_dias['middle_band'], df_ultimos_7_dias['lower_band'] = \
#                 ta.BBANDS(df_ultimos_7_dias['ask_close'], timeperiod=20)
#             if valor_actual > df_ultimos_7_dias['upper_band'][df_ultimos_7_dias.index[-1]]:
#                 indicadores_operar += 3
#                 print(f"+ Banda de Bollinger superior pasada, indicadores cumplidos = {indicadores_operar}")
#
#             if indicadores_operar >= 7:
#                 if current_order == 0:  # sin accion
#                     current_order = 1
#                     acciones.append(['buy', df_ultimos_7_dias['time'][df_ultimos_7_dias.index[-1]],
#                                      df_ultimos_7_dias['ask_close'][df_ultimos_7_dias.index[-1]]])
#
#         # else:  # TENDENCIA ALCISTA
#         #     return None
#
#         df_ultimos_7_dias['upper_band'], df_ultimos_7_dias['middle_band'], df_ultimos_7_dias['lower_band'] = \
#             ta.BBANDS(df_ultimos_7_dias['ask_close'], timeperiod=20)
#         len_x = range(len(df_ultimos_7_dias))
#         plt.plot(len_x, df_ultimos_7_dias['ask_close'])
#         plt.plot(len_x, df_ultimos_7_dias['upper_band'])
#         plt.plot(len_x, df_ultimos_7_dias['lower_band'])
#         if media_calculada:
#             plt.plot(len_x, df_ultimos_7_dias['SMA'])
#         if objetivo_cumplido:
#             plt.axvspan(intervalos[-1][0] + horas_hasta_completo - hours,
#                         intervalos[-1][-1] + horas_hasta_completo - hours, facecolor='b', alpha=0.5)
#         plt.show()
#
#         # Simulo que pasa una hora (estoy en backtesting)
#         hours += 1
#         time.sleep(0.2)
#
#     # Devuelvo el vector de acciones realizadas con su precio y datetime
#     return acciones, df_ultimos_7_dias['ask_close'][df_ultimos_7_dias.index[-1]]
#
#
# inicio = datetime.datetime(2019, 3, 22, 10)
# horas = 80
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
# beneficios = get_actions_results(acciones, ultimo_precio)
#
# print(acciones, ultimo_precio, beneficios)