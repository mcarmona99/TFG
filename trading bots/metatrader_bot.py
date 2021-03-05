# Ejemplo bot trading
from datetime import datetime, timedelta

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd

# Documentacion del modulo:
# https://pypi.org/project/MetaTrader5/#description
# https://www.mql5.com/en/docs/integration/python_metatrader5


# Conectarse a MetaTrader5
# Por defecto, si tenemos MT5 abierto con la cuenta iniciada, esto funciona, si no,
# https://www.mql5.com/es/docs/integration/python_metatrader5/mt5initialize_py
# initialize(
#    path,                     // ruta al archivo EXE del terminal MetaTrader 5
#    login=LOGIN,              // número de cuenta
#    password="PASSWORD",      // contraseña
#    server="SERVER",          // nombre del servidor como se ha establecido en el terminal
#    timeout=TIMEOUT,          // timeout
#    portable=False            // modo portable
#    )
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# request connection status and parameters
print(mt5.terminal_info())

# get data on MetaTrader 5 version
print(mt5.version())

CAMBIO = "EURAUD"
# request 1000 ticks
ticks = mt5.copy_ticks_range(CAMBIO, datetime.now()-timedelta(days=1), datetime.now(), mt5.COPY_TICKS_ALL)

# UNA VEZ HEMOS ACABADO DE RECOGER INFORMACION:
# shut down connection to MetaTrader 5
mt5.shutdown()

# DATA
print("\n----MOSTRANDO DATOS----\n")
print('ticks(', len(ticks), ')')
for val in ticks[:10]:
    print(val)

# PLOT
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(ticks)

# convert time in seconds into the datetime format
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
# display ticks on the chart
plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')

# display the legends
plt.legend(loc='upper left')

# add the header
plt.title(f'{CAMBIO} ticks')

# display the chart
plt.show()
