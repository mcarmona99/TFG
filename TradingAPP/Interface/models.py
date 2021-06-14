from io import StringIO

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from django.db import models

from .backend import utils


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

    def return_graph_range(self, start, end):
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()

        start = utils.transform_date(start)
        end = utils.transform_date(end)

        # DATA
        ticks = mt5.copy_ticks_range(self.nombre, start, end, mt5.COPY_TICKS_ALL)

        # Cuando tenemos los datos, cerramos mt5
        mt5.shutdown()

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
