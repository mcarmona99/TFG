from datetime import datetime
from io import StringIO

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from django.db import models


class Currencies(models.Model):
    pair_name = models.CharField(max_length=200)

    def __str__(self):
        return self.pair_name

    def return_graph_range(self, start, end):
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()

        # Transformar cada fecha de datetime-local a datetime
        def transform_date(date):
            date_processing = date.replace('T', '-').replace(':', '-').split('-')
            date_processing = [int(v) for v in date_processing]
            return datetime(*date_processing)

        start = transform_date(start)
        end = transform_date(end)

        # DATA
        ticks = mt5.copy_ticks_range(self.pair_name, start, end, mt5.COPY_TICKS_ALL)

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
        plt.title(f'{self.pair_name} ticks')

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        graph = imgdata.getvalue()
        return graph
