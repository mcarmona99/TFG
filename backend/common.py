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
