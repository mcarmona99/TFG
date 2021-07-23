import MetaTrader5 as mt5


def terminar_proceso_mt5():
    # Matamos el proceso del terminal de MetaTrader5, para evitar que una cuenta inexistente en el terminal no nos deje
    # incluir otra nueva
    import wmi
    # Por defecto MetaTrader5 se instala en "C:\Program Files\MetaTrader 5\terminal64.exe"
    # el proceso a terminar será terminal64.exe
    nombre = "terminal64.exe"
    # Inicializo el objeto wmi
    procesos_mt5 = wmi.WMI().Win32_Process(name=nombre)

    # Termino todos los procesos de MT5 (a efectos prácticos, solo habrá uno)
    for proceso in procesos_mt5:
        proceso.Terminate()


def login_mt5(account, password, servidor, sesion_actual):
    # establecemos la conexión con el terminal MetaTrader 5
    print(f"Versión del paquete MetaTrader5: {mt5.__version__}")
    if not mt5.initialize():
        error_text = f"initialize() falló, código de error: {mt5.last_error()}"
        print(error_text)
        terminar_proceso_mt5()
        return 1, error_text

    # La contraseña se tomará de la base de datos del terminal, si se ha indicado que se guarden los datos de conexión
    # ahora, conectamos con la cuenta indicando usuario, contraseña y servidor
    # Valido tanto para comercial como demo
    authorized = mt5.login(account, password=password, server=servidor)
    if authorized:
        success_text = f"Conectado a la cuenta #{account}"
        print(success_text)

        # mostramos los datos sobre la cuenta comercial en forma de lista
        print(f"Mostrando datos sobre la cuenta:\n{mt5.account_info()._asdict()}")

        sesion_actual.logued_MT5 = True
        sesion_actual.save()
    else:
        error_text = f"Error al intentar conectar a la cuenta #{account}, código de error: {mt5.last_error()}"
        print(error_text)
        mt5.shutdown()
        terminar_proceso_mt5()
        return 1, error_text
    return 0, success_text


def logout_mt5(sesion_actual):
    # finalizamos la conexión con el terminal MetaTrader 5
    print("Cerrando la conexión con el terminal MetaTrader5...")
    mt5.shutdown()
    terminar_proceso_mt5()
    sesion_actual.logued_MT5 = False
    sesion_actual.save()
