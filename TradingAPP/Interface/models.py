import datetime
from io import StringIO

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from matplotlib.dates import date2num, DateFormatter
from mplfinance.original_flavor import candlestick_ohlc

from .backend import utils, common


# Create your models here.

class Sesion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    algoritmo_elegido = models.ForeignKey('AlgoritmoTrading', on_delete=models.SET_NULL, null=True)
    logued_MT5 = models.BooleanField(default=False)

    def __str__(self):
        return self.user.__str__()


@receiver(post_save, sender=User)
def create_user_sesion(sender, instance, created, **kwargs):
    if created:
        Sesion.objects.create(user=instance)


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

    def obtener_grafico_datos_tiempo_real(self, marco_tiempo='1H', titulo="Gráfico OHLC"):
        # Obtengo un rago de 2 meses, para que sea valido para todos los marcos de tiempo
        ahora = datetime.datetime.now()
        inicio = ahora - datetime.timedelta(days=60)

        # Inicializo MT5
        mt5.initialize()

        # DATA
        ticks = mt5.copy_ticks_range(self.nombre, inicio, ahora, mt5.COPY_TICKS_ALL)

        # Create DataFrame out of the obtained data
        df = common.ticks_to_df_with_time(ticks)

        # Obtener los datos en formato ohlc (velas)
        df = common.transform_data_to_ohlc(df, marco_tiempo=marco_tiempo)

        # Elimino fines de semana
        df = df[df.time.dt.weekday < 5]

        # TOMO SOLO 24 VELAS, QUE ES LO QUE VOY A MOSTRAR
        df = df[-24:]
        df.reset_index(level=0, inplace=True)

        # Creo la variable necesaria para la funcion candlestick_ohlc
        data_array = [[date2num(rev.time), rev['ask_open'], rev['ask_high'], rev['ask_low'], rev['ask_close']] for
                      index, rev in df.iterrows()]

        # Genero el plot con su personalización
        # multiplicador es la variable para modificar width
        multiplicador = int(marco_tiempo.replace('H', '')) if 'H' in marco_tiempo else \
            int(marco_tiempo.replace('D', '')) * 24 if 'D' in marco_tiempo else \
                int(marco_tiempo.replace('Min', '')) / 60 if 'Min' in marco_tiempo else 1

        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.3, left=0.2)
        candlestick_ohlc(ax, data_array, width=0.015 * multiplicador, colorup='green', colordown='red')
        plt.setp(plt.gca().get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.title(f"{titulo} - {self.nombre} - {marco_tiempo}")
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M  %d-%m-%y'))
        plt.ylabel("Precio de compra")

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        grafico = imgdata.getvalue()
        print(df)
        return grafico, f"Mostrando desde {df.at[0, 'time']} hasta {df.at[len(df) - 1, 'time']}\n" \
                        f"Actualizando gráfico en {marco_tiempo} ..."

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
                        f"{start + datetime.timedelta(hours=flag + 24)}"
