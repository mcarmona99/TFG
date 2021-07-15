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
# class WyckoffTradingBacktesting:
#     def __init__(self):
#         # Variable a devolver, con accion, precio y tiempo al que la hicimos
#         self.acciones = []
#         # Variable inicial para controlar si estoy comprando o vendiendo
#         self.accion_actual = 0  # 0 = nada, 1 = buy, 2 = sell
#         self.intervalo = []
#         self.tendencia = ''
#         self.objetivo_cumplido = False  # Test 1 compra
#         self.puntos_clave_calculados = False  # Test 2 compra
#         self.secondary_test_encontrado = False  # Test 2 compra
#         self.media_calculada = False
#         self.tendencia_rota = False  # Test 4 compra
#         self.indicadores_operar = 0
#         self.ultimo_maximo = 0.0
#         self.ultimo_minimo = 0.0
#         self.flag = 0  # Flag usado para saltarme fines de semana en la adaptación de datos
#         self.zona_inferior = []
#         self.zona_superior = []
#         self.stop_lose = None
#         self.take_profit = None
#         self.dataframe = None
#         self.valor_actual = 0
#         self.punto_compra = None
#
#     def reiniciar_analisis(self, acciones=None):
#         self.acciones = acciones if acciones else []
#         self.accion_actual = 0
#         self.intervalo = []
#         self.tendencia = ''
#         self.objetivo_cumplido = False
#         self.puntos_clave_calculados = False
#         self.secondary_test_encontrado = False
#         self.media_calculada = False
#         self.tendencia_rota = False
#         self.indicadores_operar = 0
#         self.ultimo_maximo = 0.0
#         self.ultimo_minimo = 0.0
#         self.flag = 0
#         self.zona_inferior = []
#         self.zona_superior = []
#         self.stop_lose = None
#         self.take_profit = None
#         self.dataframe = None
#         self.valor_actual = 0
#         self.punto_compra = None
#
#     def inicializar_valor_actual(self):
#         self.valor_actual = self.dataframe['ask_close'][self.dataframe.index[-1]]
#
#     def imprimir_dataframe(self, intervalos, horas_hasta_completo, hours, horas_hasta_compra = 0, ver_bandas_bollinguer=False):
#         len_x = range(len(self.dataframe))
#         if ver_bandas_bollinguer:
#             self.dataframe['upper_band'], self.dataframe['middle_band'], self.dataframe['lower_band'] = \
#                 ta.BBANDS(self.dataframe['ask_close'], timeperiod=20)
#             plt.plot(len_x, self.dataframe['upper_band'])
#             plt.plot(len_x, self.dataframe['lower_band'])
#         plt.plot(len_x, self.dataframe['ask_close'])
#         if self.media_calculada and self.accion_actual == 0:
#             plt.plot(len_x, self.dataframe['SMA'])
#         if self.objetivo_cumplido:
#             plt.axvspan(intervalos[-1][0] + horas_hasta_completo - hours,
#                         intervalos[-1][-1] + horas_hasta_completo - hours, facecolor='b', alpha=0.5)
#         if self.punto_compra:
#             plt.plot(self.punto_compra[0] + horas_hasta_compra - hours, self.punto_compra[1], marker="^", c='purple', label='Compra')
#         if self.stop_lose:
#             plt.axhline(y=self.stop_lose, c="red", label='Stop Lose')
#         if self.take_profit:
#             plt.axhline(y=self.take_profit, c="green", label='Take Profit')
#         plt.legend()
#         plt.show()
#
#     def comprobar_objetivo_cumplido(self):
#         # Obtenemos en tiempo real un objetivo cumplido, alcista o bajista
#
#         # Bandas de Bollinger con media movil de 20 (middle_band)
#         self.dataframe['upper_band'], self.dataframe['middle_band'], self.dataframe['lower_band'] = \
#             ta.BBANDS(self.dataframe['ask_close'], timeperiod=20)
#         # idea para ver acumulaciones, distribuciones y tendencias con bollinger
#         # columna diferencia de upper_band con lower_band, menores diferencias implican que el mercado está lateral
#         # grandes diferencias arriba - abajo implica alcista
#         # grandes diferencias abajo - arriba implica bajista
#         # esto se puede ver si probamos a detectar anomalias en la columna pasada a numpy list
#
#         diferencia_bandas = self.dataframe['upper_band'].to_numpy() - self.dataframe['lower_band'].to_numpy()
#         diferencia_bandas = np.array(diferencia_bandas)
#
#         # DETECTO LAS ANOMALIAS DE LA DIFERENCIA DE LAS BANDAS, ESTO ME DARA INTERVALOS DE CRECIMIENTO Y DECRECIMIENTO
#         media_de_diferencias = np.mean(diferencia_bandas[~np.isnan(diferencia_bandas)])
#         anomalias = [i if not np.isnan(i) and i > media_de_diferencias else np.nan for i in diferencia_bandas]
#         indices_anomalias = [indice if not np.isnan(a) else np.nan for indice, a in enumerate(anomalias)]
#
#         intervalos = []
#         intervalo = []
#         intervalos_indice_global = []
#         intervalo_i_global = []
#         for i in indices_anomalias:
#             if not np.isnan(i):
#                 intervalo.append(i)
#                 intervalo_i_global.append(self.dataframe.index[i])
#             else:
#                 if intervalo:
#                     intervalos.append(intervalo)
#                     intervalos_indice_global.append(intervalo_i_global)
#                     intervalo_i_global = []
#                     intervalo = []
#
#         # Tengo los intervalos de crecimiento y decrecimiento
#         for intervalo_i_global in intervalos_indice_global:
#             self.objetivo_cumplido = self.dataframe.index[-2] in intervalo_i_global
#
#         self.intervalo = intervalos_indice_global[-1]
#         return intervalos
#
#     def test_compra_wyckoff(self):
#         # Si el nuevo punto está por debajo de la zona considerada para ST,
#         # ignoro este rango de acumulación ya que supongo que aún no es uno bueno para compra
#         # Reinicio la clase y vuelvo a buscar un objetivo bajista o alcista cumplido
#         if self.puntos_clave_calculados and self.valor_actual < self.zona_inferior[0]:
#             # Corresponde al test 9, se ha creado un suelo
#             # (si se ha creado, nunca llegamos a reiniciar el analisis)
#             self.reiniciar_analisis(self.acciones)
#             print("DECISION: reinicio el análisis, no se ve una acumulación clara")
#             return
#
#         if self.puntos_clave_calculados and not self.secondary_test_encontrado:
#             # Compruebo si el valor actual es un ST
#             if self.zona_inferior[0] < self.valor_actual < self.zona_inferior[1]:
#                 self.secondary_test_encontrado = True
#                 self.indicadores_operar += 1
#                 print(
#                     f"- PS, SC, AR y ST encontrados después del objetivo bajista, indicadores cumplidos = {self.indicadores_operar}")
#
#         if not self.puntos_clave_calculados:
#             # 1- El objetivo potencial bajista ya se ha cumplido
#             self.indicadores_operar += 1
#             print(f"- Objetivo potencial bajista cumplido, indicadores cumplidos = {self.indicadores_operar}")
#
#             # 2- PS, SC, AR y ST
#             # SC: selling climax
#             vector_sc = [valor for valor in [self.dataframe.loc[i, 'ask_close'] for i in self.intervalo]]
#             selling_climax = min(vector_sc)
#             indice_sc = self.intervalo[vector_sc.index(selling_climax)]
#
#             # AR: automatic rally, será el maximo obtenido despues del SC en lo que consideramos
#             # la tendencia, que la hemos sacado con anomalias
#             vector_ar = [valor for valor in
#                          [self.dataframe.loc[i, 'ask_close'] for i in
#                           self.intervalo[self.intervalo.index(indice_sc):]]]
#             automatic_rally = max(vector_ar)
#
#             self.ultimo_minimo = selling_climax
#             self.ultimo_maximo = automatic_rally
#
#             # ST: Declaro rangos o zonas para determinar STs
#             ar_menos_sc = automatic_rally - selling_climax
#
#             # La zona marcada en el SC será un 20 % arriba y abajo de la línea inferior
#             # que hace de suelo
#             tam_rango = 0.2 * ar_menos_sc
#             self.zona_inferior = [selling_climax - tam_rango, selling_climax + tam_rango]
#
#             # Hago lo mismo para la superior, aunque no se usa para los STs
#             self.zona_superior = [automatic_rally - tam_rango, automatic_rally + tam_rango]
#
#             self.puntos_clave_calculados = True
#
#         # 4- La tendencia bajista se ha roto
#         # (es decir, línea de oferta o línea de tendencia bajista ha sido rota)
#         # Implementado con media movil
#         self.dataframe['SMA'] = ta.SMA(self.dataframe.ask_close.values, 10)  # 21 periodos
#         self.media_calculada = True
#
#         if not self.tendencia_rota and self.valor_actual > self.dataframe['SMA'][self.dataframe.index[-1]]:
#             # La tendencia bajista se ha roto
#             self.indicadores_operar += 1
#             print(f"- Tendencia bajista se ha roto, indicadores cumplidos = {self.indicadores_operar}")
#             self.tendencia_rota = True
#
#         # 5- Minimos mas altos
#         if self.ultimo_minimo < self.valor_actual < self.ultimo_maximo:
#             self.indicadores_operar += 1
#             print(f"- Minimo mas alto, indicadores cumplidos = {self.indicadores_operar}")
#             self.ultimo_minimo = self.valor_actual
#
#         # 6- Maximos mas altos
#         elif self.valor_actual > self.ultimo_maximo:
#             self.indicadores_operar += 1
#             print(f"- Maximo mas alto, indicadores cumplidos = {self.indicadores_operar}")
#             self.ultimo_maximo = self.valor_actual
#
#         # COMPRO SI HE CUMPLIDO LOS INDICADORES
#         if self.indicadores_operar == 5:
#             # TODO ME FALTAN LOS TESTS 3 y 7
#             # A OJOS DE LA IMPLEMENTACION, EL NUMERO DE TESTS MAXIMO ES 7
#             if self.accion_actual == 0:  # sin accion
#                 self.accion_actual = 1  # compro
#                 self.punto_compra = [len(self.dataframe), self.valor_actual]
#                 self.stop_lose = self.zona_inferior[0]
#                 # El take profit debe ser x 3, pero pongo x 2 para ver resultados mas facilmente
#                 self.take_profit = (self.valor_actual - self.stop_lose) * 2 + self.valor_actual
#                 print("DECISION: Decido comprar tras superar los tests de Wyckoff")
#                 print(f"SL = {self.stop_lose},  TP = {self.take_profit}, valor actual = {self.valor_actual}")
#                 # ACCION, TIMESTAMP, VALOR_ACTUAL, STOP_LOSE, TAKE_PROFIT
#                 self.acciones.append(['buy', self.dataframe['time'][self.dataframe.index[-1]],
#                                       f"Valor compra = {self.valor_actual}",
#                                       f"SL = {self.stop_lose}",
#                                       f"TP = {self.take_profit}"])
#
#
# def metodo_wyckoff_backtesting(data, start_date=None, time_trading_in_hours=None, imprimir_plot_por_hora=False):
#     """
#     TODO: Docstring
#     """
#     # Inicializo clase para parametros de Trading (TODO)
#     WTB = WyckoffTradingBacktesting()
#
#     # Repetir time_trading_in_hours horas nuestro algoritmo
#     hours = 0
#     while hours < time_trading_in_hours:
#         # Adapto los datos para no coger toda la data
#         # df tendra los datos desde que tenemos datos (2011, por ejemplo), hasta start_date,
#         # que es la fecha en la que empezaríamos a operar + horas que llevamos
#         df = adapt_data_to_backtesting(data, start_date + datetime.timedelta(hours=hours + WTB.flag))
#         if (start_date + datetime.timedelta(hours=hours + WTB.flag)).weekday() >= 5:
#             WTB.flag += 48
#         df = df[df.time.dt.weekday < 5]  # Elimino fines de semana
#
#         # Cojo datos de la ultima semana para ver tendencias
#         df_ultimos_7_dias = df.tail(24 * 7)
#         WTB.dataframe = df_ultimos_7_dias
#         WTB.inicializar_valor_actual()
#
#         # SI NO TENGO NINGUNA ACCION, EMPIEZO ANALISIS
#         if WTB.accion_actual == 0:
#             # NUEVE TESTS DE COMPRA/VENTA DE WYCKOFF para una acumulación/distribución
#
#             # 1- El objetivo potencial bajista/alcista ya se ha cumplido – Gráfico de P&F/Bollinger
#             # vemos la ultima tendencia
#             if not WTB.objetivo_cumplido:
#                 intervalos = WTB.comprobar_objetivo_cumplido()
#                 horas_hasta_completo = hours
#
#             # El objetivo se ha cumplido, vemos si el intervalo del que venimos es alcista o bajista
#             if WTB.objetivo_cumplido and not WTB.tendencia:
#                 WTB.tendencia = BAJISTA if WTB.dataframe.loc[WTB.intervalo[0], 'ask_close'] - \
#                                            WTB.dataframe.loc[WTB.intervalo[-1], 'ask_close'] > 0 \
#                     else ALCISTA
#
#             # Si la tendencia ha sido bajista, 9 test de compra en una acumulación
#             if WTB.tendencia == BAJISTA:
#                 WTB.test_compra_wyckoff()
#                 if WTB.accion_actual == 1:
#                     horas_hasta_compra = hours
#
#             # else:  # TENDENCIA ALCISTA
#             #     return None
#
#         # DIBUJAR EL PLOT POR HORA,
#         # SEA CUAL SEA LA ACCION O SI ESTOY EN FASE DE ANALISIS O NO
#         if imprimir_plot_por_hora:
#             WTB.imprimir_dataframe(intervalos, horas_hasta_completo, hours)
#
#         # Simulo que pasa una hora (estoy en backtesting)
#         if WTB.accion_actual == 1:
#             if WTB.valor_actual <= WTB.stop_lose:
#                 print("ORDEN FALLIDA, HEMOS LLEGADO AL STOP LOSE")
#                 WTB.imprimir_dataframe(intervalos, horas_hasta_completo, hours, horas_hasta_compra=horas_hasta_compra)
#                 WTB.acciones[len(WTB.acciones) - 1].extend(['FALLIDA'])
#                 WTB.reiniciar_analisis(WTB.acciones)
#             elif WTB.valor_actual >= WTB.take_profit:
#                 print("ORDEN ACERTADA, HEMOS LLEGADO AL TAKE PROFIT")
#                 WTB.imprimir_dataframe(intervalos, horas_hasta_completo, hours, horas_hasta_compra=horas_hasta_compra)
#                 WTB.acciones[len(WTB.acciones) - 1].extend(['ACIERTO'])
#                 WTB.reiniciar_analisis(WTB.acciones)
#         hours += 1
#         # input(" INTRO ")
#
#     # Devuelvo el vector de acciones realizadas con su precio y datetime
#     return WTB.acciones
#
#
# inicio = datetime.datetime(2020, 5, 26, 7)
# horas = 200
# nombre_mercado = 'EURUSD'
#
# # Recogida de datos del simbolo a tratar
# # en formato ohlc con columnas
# # time  ask_open  ask_high  ask_low  ask_close  bid_open  bid_high  bid_low  bid_close
# data = get_data_ohlc(nombre_mercado)
#
# acciones = metodo_wyckoff_backtesting(data,
#                                       start_date=inicio,
#                                       time_trading_in_hours=int(horas))
# print(acciones)
