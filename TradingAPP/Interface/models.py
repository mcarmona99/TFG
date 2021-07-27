import datetime
from io import StringIO

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from django.db import models
from matplotlib.dates import date2num, DateFormatter
from mplfinance.original_flavor import candlestick_ohlc

from .backend import utils, common


# Create your models here.

class Sesion(models.Model):
    algoritmo_elegido = models.ForeignKey('AlgoritmoTrading', on_delete=models.SET_NULL, null=True)
    logued_MT5 = models.BooleanField(default=True)

    def __str__(self):
        return self.algoritmo_elegido.__str__()


class AlgoritmoTrading(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=10000)
    autor = models.CharField(max_length=200)
    imagen = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Mercado(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    def obtener_grafico_tiempo_real(self, start, end):
        # TODO FUNCION A MODIFICAR
        start = utils.transform_date(start)
        end = utils.transform_date(end)

        # DATA
        ticks = mt5.copy_ticks_range(self.nombre, start, end, mt5.COPY_TICKS_ALL)

        # Create DataFrame out of the obtained data
        ticks_frame = pd.DataFrame(ticks)

        # Convert time in seconds into the datetime format
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

        fig = plt.figure()

        # Display ticks on the chart
        plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
        plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')

        # Display the legends
        plt.legend(loc='upper left')

        # add the header
        plt.title(f'{self.nombre} ticks')

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        graph = imgdata.getvalue()
        return graph

    def obtener_grafico_datos_antiguos(self, start="", end="", horas=0, titulo="Gráfico OHLC", flag=0):
        start = utils.transform_date(start)
        if end:
            end = utils.transform_date(end)

        # Obtener los datos en formato ohlc (velas)
        data = common.get_data_ohlc(self.nombre)
        data = data[data.time.dt.weekday < 5]

        # Adaptamos los datos al rango que tenemos, df sera un dataframe de pandas con todas las horas desde start
        # hasta end o desde start hasta el numero horas dado
        df = common.adapt_data_to_range(data, start, start + datetime.timedelta(
            hours=horas)) if horas else common.adapt_data_to_range(data, start, end)

        # Creo la variable necesaria para la funcion candlestick_ohlc
        data_array = [[date2num(rev.time), rev['ask_open'], rev['ask_high'], rev['ask_low'], rev['ask_close']] for
                      index, rev in df[flag:24 + flag].iterrows()]

        # Genero el plot con su personalización
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.3, left=0.2)
        candlestick_ohlc(ax, data_array, width=0.015, colorup='green', colordown='red')
        plt.setp(plt.gca().get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.title(f"{titulo} - {self.nombre}")
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M  %d-%m-%y'))
        plt.ylabel("Precio de compra")

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        grafico = imgdata.getvalue()
        return grafico, f"Mostrando desde {start + datetime.timedelta(hours=flag)} hasta " \
                        f"{start + datetime.timedelta(hours=flag+24)}"
