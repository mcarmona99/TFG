import datetime
import os

import MetaTrader5 as mt5
import pandas as pd


def initialize_mt5():
    print("Inicializando MetaTrader5")
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        exit(1)


def get_ticks_year(ini_year, symbol):

    # copio ticks del simbolo en cuestion
    print(f"Copiando ticks de {symbol}, para año {ini_year} ...")

    # obtener ticks en el rango del año y crear dataframe
    start_data = datetime.datetime(ini_year, 1, 1)
    end_data = datetime.datetime(ini_year + 1, 1, 1)

    ticks = mt5.copy_ticks_range(symbol, start_data, end_data, mt5.COPY_TICKS_ALL)

    # array de ticks:    (1584648312, 1.06769, 1.06771, 0.,   0,      1584648312000, 134,   0.         )
    # representan:       (time,       bid,     ask,     last, volume, time_msc,      flags, volume_real)

    return ticks


def ticks_to_df(ticks):
    ticks_df = pd.DataFrame(ticks)
    try:
        print("Creando DataFrame de Pandas...")
        ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')
        ticks_df = ticks_df.set_index(['time'])
        return ticks_df
    except KeyError:
        return None


def get_data_ohlc(data_frame):
    # Uso la funcion ohlc de pandas para generar las velas, la salida sera similar a:
    #
    # time                  open    high    low     close
    # 2016-01-04 00:00:00   87.651  87.696  87.630  87.687
    # ...
    #
    # En este caso, velas de rango 1 hora

    data_ask = data_frame['ask'].resample('1H').ohlc()
    data_bid = data_frame['bid'].resample('1H').ohlc()
    data_ask_bid = pd.concat([data_ask, data_bid], axis=1, keys=['Ask', 'Bid'])

    return data_ask_bid


if __name__ == '__main__':
    # Obtenemos datos de los siguientes 5 mercados que vamos a tener en cuenta
    symbol_names = ['EURUSD', 'XAUUSD', 'XAGEUR', 'XNGUSD', 'XBRUSD']
    symbol_paths = ['Forex\\Majors\\EURUSD',
                    'Commodities\\Metals\\XAUUSD',
                    'Commodities\\Metals\\XAGEUR',
                    'Commodities\\Energies\\Energies Spot\\XNGUSD',
                    'Commodities\\Energies\\Energies Spot\\XBRUSD']

    initialize_mt5()

    for symbol, symbol_path in zip(symbol_names, symbol_paths):
        for year in range(2010, 2022):
            if os.path.exists(f"{symbol_path}_{year}.csv"):
                print(f"Ticks ya copiados: {symbol} para año {year}")
            else:
                ticks = get_ticks_year(year, symbol)
                if ticks is not None:
                    if len(ticks) != 0:
                        ticks_df = ticks_to_df(ticks)
                        data_ohlc = get_data_ohlc(ticks_df)
                        os.makedirs(os.path.dirname(symbol_path), exist_ok=True)
                        data_ohlc.to_csv(f"{symbol_path}_{year}.csv")

    mt5.shutdown()
