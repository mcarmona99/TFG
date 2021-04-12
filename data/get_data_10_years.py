import datetime
import os

import MetaTrader5 as mt5
import pandas as pd


def get_data_year(ini_year, symbol):
    print("Abriendo MetaTrader5 ...")
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        exit(1)

    # ------------ EXTRACCION DE DATOS DE MERCADOS ------------

    # PROPIEDADES DE UTILIDAD:

    # SIMBOLOS DISPONIBLES CON LOS QUE OPERAR (mercados) -> available_symbols.txt

    # Nos centraremos en 5 mercados exclusivamente:
    # 1 forex: EURUSD ( euro vs dolar)
    # 2 metals: XAUUSD (oro vs dolar) y XAGEUR (plata vs euro)
    # 2 energy: XNGUSD (gas natural vs dolar) y XBRUSD (petroleo brent vs dolar)

    # Propiedades de cada tick de cada símbolo: ['time', 'bid', 'ask', 'last', 'volume', 'time_msc', 'flags',
    # 'volume_real']

    """
    Guardo los datos de cada mercado de MT5
    """

    symbol = mt5.symbols_get(symbol)[0]
    symbol_path = symbol.path
    if os.path.exists(f"{symbol_path}_{ini_year}.csv"):
        print(f"Ticks ya copiados: {symbol.path}")
        mt5.shutdown()
        return None
    else:
        # copio ticks del simbolo en cuestion
        print(f"Copiando ticks de {symbol.path} ...")

        # crear directorios con symbol path
        os.makedirs(os.path.dirname(symbol_path), exist_ok=True)

        # obtener ticks en el rango de YEARS años y crear dataframe
        print(f"Recogiendo datos de año {ini_year}")
        end_data = datetime.datetime(ini_year + 1, 1, 1)
        start_data = datetime.datetime(ini_year, 1, 1)

        ticks = mt5.copy_ticks_range(symbol.name, start_data, end_data, mt5.COPY_TICKS_ALL)

        # array de ticks:    (1584648312, 1.06769, 1.06771, 0.,   0,      1584648312000, 134,   0.         )
        # representan:       (time,       bid,     ask,     last, volume, time_msc,      flags, volume_real)

        # UNA VEZ HEMOS ACABADO DE RECOGER INFORMACION:
        # shut down connection to MetaTrader 5
        mt5.shutdown()
        return ticks


def ticks_to_df_with_time(ticks):
    ticks_df = pd.DataFrame(ticks)

    try:
        print("Creando DataFrame de Pandas...")
        ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')

        # creo una columna en el dataframe con la fecha sin minutos y segundos (solo la hora), para
        # quitar ticks duplicados en la misma hora, quedandome solo con el primero de cada hora
        ticks_df['time'] = pd.to_datetime(ticks_df['time'].dt.date) + \
                           pd.to_timedelta(ticks_df['time'].dt.hour, unit='H')

        ticks_df.drop_duplicates(subset='time', keep='first', inplace=True)
        return ticks_df
    except KeyError:
        return None


def df_to_csv(ticks_df, symbol, year):
    if not mt5.initialize():
        mt5.shutdown()
        exit(1)
    s = mt5.symbols_get(symbol)[0]
    mt5.shutdown()

    symbol_path = s.path
    # pasar al csv de la ruta del simbolo
    ticks_df.to_csv(f"{symbol_path}_{year}.csv")


if __name__ == '__main__':
    symbols_names = ['EURUSD', 'XAUUSD', 'XAGEUR', 'XNGUSD', 'XBRUSD']

    for symbol in symbols_names:
        for year in range(2010, 2022):
            ticks = get_data_year(year, symbol)
            if ticks is not None:
                if len(ticks) != 0:
                    ticks_df = ticks_to_df_with_time(ticks)
                    df_to_csv(ticks_df, symbol, year)
