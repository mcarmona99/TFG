import datetime

import MetaTrader5 as mt5
import pandas as pd

from .common import transform_data_to_ohlc


def get_data_year(ini_year, symbol):
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
    # obtener ticks en el rango de YEARS años y crear dataframe
    end_data = datetime.datetime(ini_year + 1, 1, 1)
    start_data = datetime.datetime(ini_year, 1, 1)

    ticks = mt5.copy_ticks_range(symbol, start_data, end_data, mt5.COPY_TICKS_ALL)

    # array de ticks:    (1584648312, 1.06769, 1.06771, 0.,   0,      1584648312000, 134,   0.         )
    # representan:       (time,       bid,     ask,     last, volume, time_msc,      flags, volume_real)

    # UNA VEZ HEMOS ACABADO DE RECOGER INFORMACION:
    # shut down connection to MetaTrader 5
    mt5.shutdown()
    return ticks


def ticks_to_df_with_time(ticks, from_app=False):
    ticks_df = pd.DataFrame(ticks)

    try:
        ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')

        if not from_app:
            # creo una columna en el dataframe con la fecha sin minutos y segundos (solo la hora), para
            # quitar ticks duplicados en la misma hora, quedandome solo con el primero de cada hora
            ticks_df['time'] = pd.to_datetime(ticks_df['time'].dt.date) + \
                               pd.to_timedelta(ticks_df['time'].dt.hour, unit='H')

            ticks_df.drop_duplicates(subset='time', keep='first', inplace=True)

        return ticks_df
    except KeyError:
        return None


def get_data_csv_ohlc(ano_inicio, simbolo, marco_tiempo, from_app=True):
    ano_actual = datetime.datetime.now().year + 1
    ano_inicio = int(ano_inicio)
    data_final = None
    for year in range(ano_inicio, ano_actual):
        ticks = get_data_year(year, simbolo)
        if ticks is not None:
            if len(ticks) != 0:
                ticks_df = ticks_to_df_with_time(ticks, from_app=from_app)
                if data_final is None:
                    data_final = ticks_df
                else:
                    data_final = pd.concat([data_final, ticks_df])

    data_final = transform_data_to_ohlc(data_final, marco_tiempo, from_app=from_app)
    # Guardo data en la base de datos
    from io import StringIO
    s = StringIO()
    print('Dataframe guardado:')
    print(data_final)
    data_final.to_csv(s)
    return s.getvalue()
