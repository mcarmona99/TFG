# Archivo usado para variables y funciones comunes a todos los scripts

import datetime
import os
import re

import MetaTrader5 as mt5
import pandas as pd

from data.get_data_10_years import ticks_to_df_with_time

# VARIABLES

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')


# FUNCIONES

def find_files_regex(filename, search_path):
    """
    TODO: Docstring
    """
    files_found = []
    regex = re.compile('.*{}.*'.format(filename))
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if regex.match(file):
                files_found.append(os.path.join(root, file))

    return files_found


def get_hours_from_timedelta(td):
    """
    TODO: Docstring
    """
    # Ignoro los minutos y segundos
    days, hours = td.days, td.seconds // 3600
    return hours + days * 24


def get_data(symbol, data_path=DATA_PATH):
    """
    TODO: Docstring
    """
    frames = []
    for file in find_files_regex(symbol, data_path):
        df_file = pd.read_csv(file)
        df_file['time'] = pd.to_datetime(df_file['time'], dayfirst=False, yearfirst=True)
        df_file = df_file.sort_values(by=['time'], axis=0, ascending=True)

        # Eliminar columna 0 residuo de los datos
        df_file = df_file.drop(df_file.columns[[0]], axis=1)

        frames.append(df_file)

    try:
        df = pd.concat(frames)
    except ValueError:
        print(f"No se han encontrado dataframes para {symbol} en {data_path}")
        # TODO: Gestion de errores
        return None

    return df


def update_data_to_realtime(old_dataframe, symbol):
    """
    TODO: Docstring
    """
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        exit(1)

    ticks = mt5.copy_ticks_range(symbol, old_dataframe['time'].max(), datetime.datetime.now(), mt5.COPY_TICKS_ALL)
    mt5.shutdown()

    if ticks is None:
        print("No se pudo actualizar el dataframe a tiempo real")
        # TODO: Gestion de errores
        return False

    ticks_df = ticks_to_df_with_time(ticks)

    return pd.concat([old_dataframe, ticks_df])


def adapt_data_to_backtesting(old_dataframe, end_data):
    """
    TODO: Docstring
    """
    return old_dataframe[old_dataframe['time'] < end_data]


def get_actions_results(acciones, ultimo_precio):
    comprando = False
    if acciones[0][0] == 'buy':
        comprando = True

    beneficio = 0.0
    for i in range(0, len(acciones) - 1):
        beneficio = beneficio + acciones[i + 1][2] - acciones[i][2] if comprando \
            else beneficio + acciones[i][2] - acciones[i + 1][2]
        comprando = False if comprando else True

    beneficio = beneficio + ultimo_precio - acciones[len(acciones) - 1][2] if comprando \
        else beneficio + acciones[len(acciones) - 1][2] - ultimo_precio

    return beneficio
