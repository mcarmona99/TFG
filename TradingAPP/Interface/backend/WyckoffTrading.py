import warnings

import numpy as np
import talib as ta
from matplotlib import pyplot as plt
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


class WyckoffTradingBacktesting:
    def __init__(self):
        # Variable a devolver, con accion, precio y tiempo al que la hicimos
        self.acciones = []
        # Variable inicial para controlar si estoy comprando o vendiendo
        self.accion_actual = 0  # 0 = nada, 1 = buy, 2 = sell
        self.intervalo = []
        self.tendencia = ''
        self.objetivo_cumplido = False  # Test 1 compra
        self.puntos_clave_calculados = False  # Test 2 compra
        self.secondary_test_encontrado = False  # Test 2 compra
        self.media_calculada = False
        self.tendencia_rota = False  # Test 4 compra
        self.indicadores_operar = 0
        self.ultimo_maximo = 0.0
        self.ultimo_minimo = 0.0
        self.flag = 0  # Flag usado para saltarme fines de semana en la adaptación de datos
        self.zona_inferior = []
        self.zona_superior = []
        self.stop_lose = None
        self.take_profit = None
        self.dataframe = None
        self.valor_actual = 0
        self.punto_operacion = None

    def reiniciar_analisis(self, acciones=None, flag=0):
        self.acciones = acciones if acciones else []
        self.accion_actual = 0
        self.intervalo = []
        self.tendencia = ''
        self.objetivo_cumplido = False
        self.puntos_clave_calculados = False
        self.secondary_test_encontrado = False
        self.media_calculada = False
        self.tendencia_rota = False
        self.indicadores_operar = 0
        self.ultimo_maximo = 0.0
        self.ultimo_minimo = 0.0
        self.flag = flag
        self.zona_inferior = []
        self.zona_superior = []
        self.stop_lose = None
        self.take_profit = None
        self.dataframe = None
        self.valor_actual = 0
        self.punto_operacion = None

    def inicializar_valor_actual(self):
        self.valor_actual = self.dataframe['ask_close'][self.dataframe.index[-1]]

    def imprimir_dataframe(self, intervalos, horas_hasta_completo, hours, horas_hasta_operacion=0,
                           ver_bandas_bollinguer=False):
        len_x = range(len(self.dataframe))
        if ver_bandas_bollinguer:
            self.dataframe['upper_band'], self.dataframe['middle_band'], self.dataframe['lower_band'] = \
                ta.BBANDS(self.dataframe['ask_close'], timeperiod=20)
            plt.plot(len_x, self.dataframe['upper_band'])
            plt.plot(len_x, self.dataframe['lower_band'])
        plt.plot(len_x, self.dataframe['ask_close'])
        if self.media_calculada and self.accion_actual == 0:
            plt.plot(len_x, self.dataframe['SMA'])
        if self.objetivo_cumplido:
            plt.axvspan(intervalos[-1][0] + horas_hasta_completo - hours,
                        intervalos[-1][-1] + horas_hasta_completo - hours, facecolor='b', alpha=0.5)
        if self.punto_operacion:
            plt.plot(self.punto_operacion[0] + horas_hasta_operacion - hours, self.punto_operacion[1],
                     marker="^" if self.accion_actual == 1 else "v", c='purple',
                     label='Compra' if self.accion_actual == 1 else "Venta")
        if self.stop_lose:
            plt.axhline(y=self.stop_lose, c="red", label='Stop Lose')
        if self.take_profit:
            plt.axhline(y=self.take_profit, c="green", label='Take Profit')
        plt.legend()
        plt.show()

    def comprobar_objetivo_cumplido(self):
        # Obtenemos en tiempo real un objetivo cumplido, alcista o bajista

        # Bandas de Bollinger con media movil de 20 (middle_band)
        self.dataframe['upper_band'], self.dataframe['middle_band'], self.dataframe['lower_band'] = \
            ta.BBANDS(self.dataframe['ask_close'], timeperiod=20)
        # idea para ver acumulaciones, distribuciones y tendencias con bollinger
        # columna diferencia de upper_band con lower_band, menores diferencias implican que el mercado está lateral
        # grandes diferencias arriba - abajo implica alcista
        # grandes diferencias abajo - arriba implica bajista
        # esto se puede ver si probamos a detectar anomalias en la columna pasada a numpy list

        diferencia_bandas = self.dataframe['upper_band'].to_numpy() - self.dataframe['lower_band'].to_numpy()
        diferencia_bandas = np.array(diferencia_bandas)

        # DETECTO LAS ANOMALIAS DE LA DIFERENCIA DE LAS BANDAS, ESTO ME DARA INTERVALOS DE CRECIMIENTO Y DECRECIMIENTO
        media_de_diferencias = np.mean(diferencia_bandas[~np.isnan(diferencia_bandas)])
        anomalias = [i if not np.isnan(i) and i > media_de_diferencias else np.nan for i in diferencia_bandas]
        indices_anomalias = [indice if not np.isnan(a) else np.nan for indice, a in enumerate(anomalias)]

        intervalos = []
        intervalo = []
        intervalos_indice_global = []
        intervalo_i_global = []
        for i in indices_anomalias:
            if not np.isnan(i):
                intervalo.append(i)
                intervalo_i_global.append(self.dataframe.index[i])
            else:
                if intervalo:
                    intervalos.append(intervalo)
                    intervalos_indice_global.append(intervalo_i_global)
                    intervalo_i_global = []
                    intervalo = []

        # Tengo los intervalos de crecimiento y decrecimiento
        for intervalo_i_global in intervalos_indice_global:
            self.objetivo_cumplido = self.dataframe.index[-2] in intervalo_i_global

        # Coger el último intervalo siempre y cuando no sea de longitud 1,
        # ya que sería un único valor
        for i in range(1, len(intervalos_indice_global)):
            if len(intervalos_indice_global[-i]) > 1:
                self.intervalo = intervalos_indice_global[-i]
                break
        return intervalos

    def test_compra_wyckoff(self):
        # Si el nuevo punto está por debajo de la zona considerada para ST,
        # ignoro este rango de acumulación ya que supongo que aún no es uno bueno para compra
        # Reinicio la clase y vuelvo a buscar un objetivo bajista o alcista cumplido
        if self.puntos_clave_calculados and self.valor_actual < self.zona_inferior[0]:
            # Corresponde al test 9, se ha creado un suelo
            # (si se ha creado, nunca llegamos a reiniciar el analisis)
            self.reiniciar_analisis(self.acciones, self.flag)
            print("DECISION: reinicio el análisis, no se ve una acumulación clara")
            return

        if self.puntos_clave_calculados and not self.secondary_test_encontrado:
            # Compruebo si el valor actual es un ST
            if self.zona_inferior[0] < self.valor_actual < self.zona_inferior[1]:
                self.secondary_test_encontrado = True
                self.indicadores_operar += 1
                print(
                    f"- PS, SC, AR y ST encontrados después del objetivo bajista, indicadores cumplidos = {self.indicadores_operar}")

        if not self.puntos_clave_calculados:
            # 1- El objetivo potencial bajista ya se ha cumplido
            self.indicadores_operar += 1
            print(f"- Objetivo potencial bajista cumplido, indicadores cumplidos = {self.indicadores_operar}")

            # 2- PS, SC, AR y ST
            # SC: selling climax
            vector_sc = [valor for valor in [self.dataframe.loc[i, 'ask_close'] for i in self.intervalo]]
            selling_climax = min(vector_sc)
            indice_sc = self.intervalo[vector_sc.index(selling_climax)]

            # AR: automatic rally, será el maximo obtenido despues del SC en lo que consideramos
            # la tendencia, que la hemos sacado con anomalias
            vector_ar = [valor for valor in
                         [self.dataframe.loc[i, 'ask_close'] for i in
                          self.intervalo[self.intervalo.index(indice_sc):]]]
            automatic_rally = max(vector_ar)

            self.ultimo_minimo = selling_climax
            self.ultimo_maximo = automatic_rally

            # ST: Declaro rangos o zonas para determinar STs
            ar_menos_sc = automatic_rally - selling_climax

            # La zona marcada en el SC será un 20 % arriba y abajo de la línea inferior
            # que hace de suelo
            tam_rango = 0.2 * ar_menos_sc
            self.zona_inferior = [selling_climax - tam_rango, selling_climax + tam_rango]

            # Hago lo mismo para la superior, aunque no se usa para los STs
            self.zona_superior = [automatic_rally - tam_rango, automatic_rally + tam_rango]

            self.puntos_clave_calculados = True

        # 4- La tendencia bajista se ha roto
        # (es decir, línea de oferta o línea de tendencia bajista ha sido rota)
        # Implementado con media movil
        self.dataframe['SMA'] = ta.SMA(self.dataframe.ask_close.values, 10)  # 21 periodos
        self.media_calculada = True

        if not self.tendencia_rota and self.valor_actual > self.dataframe['SMA'][self.dataframe.index[-1]]:
            # La tendencia bajista se ha roto
            self.indicadores_operar += 1
            print(f"- Tendencia bajista se ha roto, indicadores cumplidos = {self.indicadores_operar}")
            self.tendencia_rota = True

        # 5- Minimos mas altos
        if self.ultimo_minimo < self.valor_actual < self.ultimo_maximo:
            self.indicadores_operar += 1
            print(f"- Minimo mas alto, indicadores cumplidos = {self.indicadores_operar}")
            self.ultimo_minimo = self.valor_actual

        # 6- Maximos mas altos
        elif self.valor_actual > self.ultimo_maximo:
            self.indicadores_operar += 1
            print(f"- Maximo mas alto, indicadores cumplidos = {self.indicadores_operar}")
            self.ultimo_maximo = self.valor_actual

        # COMPRO SI HE CUMPLIDO LOS INDICADORES
        if self.indicadores_operar == 5:
            # TODO ME FALTAN LOS TESTS 3 y 7
            # A OJOS DE LA IMPLEMENTACION, EL NUMERO DE TESTS MAXIMO ES 7
            if self.accion_actual == 0:  # sin accion
                self.accion_actual = 1  # compro
                self.punto_operacion = [len(self.dataframe), self.valor_actual]
                self.stop_lose = self.zona_inferior[0]
                # El take profit debe ser x 3, pero pongo x 2 para ver resultados mas facilmente
                self.take_profit = (self.valor_actual - self.stop_lose) * 2 + self.valor_actual
                print("DECISION: Decido comprar tras superar los tests de Wyckoff")
                print(f"SL = {self.stop_lose},  TP = {self.take_profit}, valor actual = {self.valor_actual}")
                # ACCION, TIMESTAMP, VALOR_ACTUAL, STOP_LOSE, TAKE_PROFIT
                self.acciones.append(['buy', self.dataframe['time'][self.dataframe.index[-1]],
                                      f"Valor compra = {self.valor_actual}",
                                      f"SL = {self.stop_lose}",
                                      f"TP = {self.take_profit}"])

    def test_venta_wyckoff(self):
        # Si el nuevo punto está por encima de la zona considerada para ST,
        # ignoro este rango de distribucion ya que supongo que aún no es uno bueno para compra
        # Reinicio la clase y vuelvo a buscar un objetivo bajista o alcista cumplido
        if self.puntos_clave_calculados and self.valor_actual > self.zona_superior[1]:
            # Corresponde al test 9, se ha creado un suelo
            # (si se ha creado, nunca llegamos a reiniciar el analisis)
            self.reiniciar_analisis(self.acciones, self.flag)
            print("DECISION: reinicio el análisis, no se ve una distribución clara")
            return

        if self.puntos_clave_calculados and not self.secondary_test_encontrado:
            # Compruebo si el valor actual es un ST (lo es si esta en la zona superior)
            if self.zona_superior[0] < self.valor_actual < self.zona_superior[1]:
                self.secondary_test_encontrado = True
                self.indicadores_operar += 1
                print(
                    f"- PS, SC, AR y ST encontrados después del objetivo bajista, indicadores cumplidos = {self.indicadores_operar}")

        if not self.puntos_clave_calculados:
            # 1- El objetivo potencial alcista ya se ha cumplido
            self.indicadores_operar += 1
            print(f"- Objetivo potencial alcista cumplido, indicadores cumplidos = {self.indicadores_operar}")

            # 2- PS, BC, AR y ST
            # BC: Buying climax
            vector_bc = [valor for valor in [self.dataframe.loc[i, 'ask_close'] for i in self.intervalo]]
            buying_climax = max(vector_bc)
            indice_bc = self.intervalo[vector_bc.index(buying_climax)]

            # AR: automatic reaction, será el minimo obtenido despues del BC en lo que consideramos
            # la tendencia, que la hemos sacado con anomalias
            vector_ar = [valor for valor in
                         [self.dataframe.loc[i, 'ask_close'] for i in
                          self.intervalo[self.intervalo.index(indice_bc):]]]
            automatic_reaction = min(vector_ar)

            self.ultimo_maximo = buying_climax
            self.ultimo_minimo = automatic_reaction

            # ST: Declaro rangos o zonas para determinar STs
            bc_menos_ar = buying_climax - automatic_reaction

            # La zona marcada en el BC será un 20 % arriba y abajo de la línea superior
            # que hace de techo
            tam_rango = 0.2 * bc_menos_ar
            self.zona_inferior = [automatic_reaction - tam_rango, automatic_reaction + tam_rango]

            # Hago lo mismo para la superior, aunque no se usa para los STs
            self.zona_superior = [buying_climax - tam_rango, buying_climax + tam_rango]

            self.puntos_clave_calculados = True

        # 4- La tendencia alcista se ha roto
        # (es decir, línea de oferta o línea de tendencia alcista ha sido rota)
        # Implementado con media movil
        self.dataframe['SMA'] = ta.SMA(self.dataframe.ask_close.values, 10)  # 21 periodos
        self.media_calculada = True

        if not self.tendencia_rota and self.valor_actual < self.dataframe['SMA'][self.dataframe.index[-1]]:
            # La tendencia alcista se ha roto
            self.indicadores_operar += 1
            print(f"- Tendencia alcista se ha roto, indicadores cumplidos = {self.indicadores_operar}")
            self.tendencia_rota = True

        # 6- Maximos mas bajos
        if self.ultimo_minimo < self.valor_actual < self.ultimo_maximo:
            self.indicadores_operar += 1
            print(f"- Maximo mas bajo, indicadores cumplidos = {self.indicadores_operar}")
            self.ultimo_maximo = self.valor_actual

        # 5- Minimos mas bajos
        elif self.ultimo_minimo > self.valor_actual:
            self.indicadores_operar += 1
            print(f"- Minimo mas bajo, indicadores cumplidos = {self.indicadores_operar}")
            self.ultimo_minimo = self.valor_actual

        # COMPRO SI HE CUMPLIDO LOS INDICADORES
        if self.indicadores_operar == 5:
            # TODO ME FALTAN LOS TESTS 3 y 7
            # A OJOS DE LA IMPLEMENTACION, EL NUMERO DE TESTS MAXIMO ES 7
            if self.accion_actual == 0:  # sin accion
                self.accion_actual = 2  # venta
                self.punto_operacion = [len(self.dataframe), self.valor_actual]
                self.stop_lose = self.zona_superior[1]
                # El take profit debe ser x 3, pero pongo x 2 para ver resultados mas facilmente
                self.take_profit = self.valor_actual - (self.stop_lose - self.valor_actual) * 2
                print("DECISION: Decido vender tras superar los tests de Wyckoff")
                print(f"SL = {self.stop_lose},  TP = {self.take_profit}, valor actual = {self.valor_actual}")
                # ACCION, TIMESTAMP, VALOR_ACTUAL, STOP_LOSE, TAKE_PROFIT
                self.acciones.append(['sell', self.dataframe['time'][self.dataframe.index[-1]],
                                      f"Valor venta = {self.valor_actual}",
                                      f"SL = {self.stop_lose}",
                                      f"TP = {self.take_profit}"])
