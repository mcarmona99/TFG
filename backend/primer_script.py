# Primer script para una estrategia simple de trading
# Funciones:
# Entrada -> datos, periodo para operar y mi cartera
# Salida -> historico de movimientos durante

import pandas as pd

import common


def get_data(symbol, data_path=common.DATA_PATH):
    """
    TODO: Docstring
    """
    frames = []
    for file in common.find_files_regex(symbol, data_path):
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


if __name__ == '__main__':
    symbols_names = ['EURUSD', 'XAUUSD', 'XAGEUR', 'XNGUSD', 'XBRUSD']
    dataframes = [get_data(symbol) for symbol in symbols_names]
