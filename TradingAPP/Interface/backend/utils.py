from datetime import datetime


# Transformar cada fecha de datetime-local a datetime
def transform_date(date):
    date_processing = date.replace('T', '-').replace(':', '-').split('-')
    date_processing = [int(v) for v in date_processing]
    return datetime(*date_processing)


def acciones_to_str(acciones):
    # Formato de salida
    # ['buy', Timestamp('2021-07-29 16:00:00'),
    # 'Valor compra = 1.18796', 'SL = 1.18715',
    # 'TP = 1.1895799999999999', 'ACIERTO']
    nuevas_acciones = []
    for i in range(len(acciones)):
        nueva_accion = f"- Orden número {i + 1}: {'COMPRA' if acciones[i][0] == 'buy' else 'VENTA'}." \
                       f"\tRealizada con fecha y hora: {acciones[i][1].strftime('%d/%m %H:%M')}." \
                       f"\t{acciones[i][2]}." \
                       f"\t{acciones[i][3]}.\n\t{acciones[i][4]}.\n"
        if len(acciones[i]) >= 6:
            nueva_accion = f"{nueva_accion}\tRESULTADO: {acciones[i][5]}.\n"
        if len(acciones[i]) >= 7:
            nueva_accion = f"{nueva_accion}\tBENEFICIOS OBTENIDOS: {acciones[i][6]}.\n\n" if acciones[i][6] > 0 else \
                f"{nueva_accion}\tPÉRDIDAS OBTENIDAS: {acciones[i][6]}.\n\n"

        nuevas_acciones.append(nueva_accion)
    return nuevas_acciones


def anadir_beneficio_acciones(acciones):
    for accion in acciones:
        if len(accion) >= 6:
            valor = accion[2].replace("Valor compra = ", "")
            valor = valor.replace("Valor venta = ", "")
            sl = accion[3].replace("SL = ", "")
            tp = accion[4].replace("TP = ", "")
            if accion[5] == 'ACIERTO' and accion[0] == 'buy':
                accion.append(float(tp) - float(valor))
            if accion[5] == 'ACIERTO' and accion[0] == 'sell':
                accion.append(float(valor) - float(tp))
            if accion[5] == 'FALLIDA' and accion[0] == 'buy':
                accion.append(float(sl) - float(valor))
            if accion[5] == 'FALLIDA' and accion[0] == 'sell':
                accion.append(float(valor) - float(sl))
    return acciones


def calcular_balance(acciones):
    balance = 0.0
    for accion in acciones:
        if len(accion) >= 7:
            balance += float(accion[-1])
    return balance
