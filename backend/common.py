# Archivo usado para variables y funciones comunes a todos los scripts

import os
import re

import pandas as pd

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
