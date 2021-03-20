import datetime
import os

import MetaTrader5 as mt5
import pandas as pd

print("Abriendo MetaTrader5 ...")
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()
    exit(1)

# ------------ EXTRACCION DE DATOS DE MERCADOS ------------

# PROPIEDADES DE UN SIMBOLO (variables de la clase SimbolInfo)

# eurusd = mt5.symbol_info("EURUSD")
# symbol_info_dict = eurusd._asdict()
# for prop in symbol_info_dict:
#     print("{}={}".format(prop, symbol_info_dict[prop]))

# OUTPUT:

"""
custom=False
chart_mode=0
select=True
visible=True
session_deals=0
session_buy_orders=0
session_sell_orders=0
volume=0
volumehigh=0
volumelow=0
time=1616192707
digits=5
spread=0
spread_float=True
ticks_bookdepth=10
trade_calc_mode=0
trade_mode=4
start_time=0
expiration_time=0
trade_stops_level=0
trade_freeze_level=0
trade_exemode=2
swap_mode=1
swap_rollover3days=3
margin_hedged_use_leg=False
expiration_mode=15
filling_mode=2
order_mode=127
order_gtc_mode=0
option_mode=0
option_right=0
bid=1.19056
bidhigh=1.19372
bidlow=1.1874
ask=1.19056
askhigh=1.19372
asklow=1.1874
last=0.0
lasthigh=0.0
lastlow=0.0
volume_real=0.0
volumehigh_real=0.0
volumelow_real=0.0
option_strike=0.0
point=1e-05
trade_tick_value=1.0
trade_tick_value_profit=1.0
trade_tick_value_loss=1.0
trade_tick_size=1e-05
trade_contract_size=100000.0
trade_accrued_interest=0.0
trade_face_value=0.0
trade_liquidity_rate=0.0
volume_min=0.01
volume_max=200.0
volume_step=0.01
volume_limit=0.0
swap_long=-4.4
swap_short=-0.21
margin_initial=100000.0
margin_maintenance=0.0
session_volume=0.0
session_turnover=0.0
session_interest=0.0
session_buy_orders_volume=0.0
session_sell_orders_volume=0.0
session_open=1.19136
session_close=1.19158
session_aw=0.0
session_price_settlement=0.0
session_price_limit_min=0.0
session_price_limit_max=0.0
margin_hedged=0.0
price_change=-0.0856
price_volatility=0.0
price_theoretical=0.0
price_greeks_delta=0.0
price_greeks_theta=0.0
price_greeks_gamma=0.0
price_greeks_vega=0.0
price_greeks_rho=0.0
price_greeks_omega=0.0
price_sensitivity=0.0
basis=
category=
currency_base=EUR
currency_profit=USD
currency_margin=EUR
bank=
description=Euro vs US Dollar
exchange=
formula=
isin=
name=EURUSD
page=
path=Forex\Majors\EURUSD
"""

# PROPIEDADES DE UTILIDAD:

# spread=0
# bid=1.19056
# bidhigh=1.19372
# bidlow=1.1874
# ask=1.19056
# askhigh=1.19372
# asklow=1.1874
# volume_real=0.0
# volumehigh_real=0.0
# volumelow_real=0.0
# name=EURUSD
# path=Forex\Majors\EURUSD

# SIMBOLOS DISPONIBLES CON LOS QUE OPERAR (mercados)

# simbolos = mt5.symbols_get()
# for simbolo in simbolos:
#     print(f"{simbolo.path} -> {simbolo.description}")

# OUTPUT:

# simbol paths and names in available_symbols.txt

PROPERTIES = ['time', 'bid', 'ask', 'last', 'volume', 'time_msc', 'flags', 'volume_real']
YEARS_BEFORE = 2

symbols = mt5.symbols_get()
end_data = datetime.datetime.now()
start_data = end_data - datetime.timedelta(days=YEARS_BEFORE * 365)

"""
Creo base de datos y meto los datos de cada mercado de MT5
"""

for i, symbol in enumerate(symbols[:100]):
    # crear directorios con symbol path
    symbol_path = symbol.path
    os.makedirs(os.path.dirname(symbol_path), exist_ok=True)

    # obtener ticks en el rango y crear dataframe
    print(f"Copiando ticks de {symbol.path} ... ({i}/{len(symbols)})")
    ticks = mt5.copy_ticks_range(symbol.name, start_data, end_data, mt5.COPY_TICKS_ALL)
    ticks_df = pd.DataFrame(ticks)
    try:
        ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')

        # crear dataframe por horas, cojo las de xx:00:00,
        # quito duplicadas quedandome con las primeras
        ticks_df = ticks_df[ticks_df['time'].dt.minute == 0]
        ticks_df = ticks_df[ticks_df['time'].dt.second == 0]
        ticks_df.drop_duplicates(subset='time', keep='first', inplace=True)

        # pasar al csv de la ruta del simbolo
        ticks_df.to_csv(symbol_path)
    except KeyError:
        # mode="a" to append to error.txt
        with open("error.txt", mode="a") as f:
            f.write(f"Key Error en {symbol.name}")

# array de ticks:    (1584648312, 1.06769, 1.06771, 0.,   0,      1584648312000, 134,   0.         )
# representan:       (time,       bid,     ask,     last, volume, time_msc,      flags, volume_real)

# UNA VEZ HEMOS ACABADO DE RECOGER INFORMACION:
# shut down connection to MetaTrader 5
mt5.shutdown()
