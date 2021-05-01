import requests
import datetime
import os
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.messagebox import showinfo

## when dropdown menu option is selected, 'desplegar_frame_seleccionado' is called
def desplegar_frame_seleccionado( selector, rootWidget ):
   
    if selector == 'Recibir Cantidad':
        ## If 'Recibir Cantidad' selected, actuators are shown

        ## Control Label to check if selection is correct
        #labelTest.configure( text = "Recibir Cantidad" )

        ## Text entry for amount crypto
        string_recibir_cry = tk.StringVar( frame_recibir_cantidad )
        textbox_recibir_cantidad_cry = tk.Entry( frame_recibir_cantidad, textvariable = string_recibir_cry, state = 'normal' )
        textbox_recibir_cantidad_cry.insert( 0, '' )
        textbox_recibir_cantidad_cry.grid( row = 2, column = 2, padx = 10 )
        
        ## Text entry for amount usd
        string_recibir_usd = tk.StringVar( frame_recibir_cantidad )
        textbox_recibir_cantidad_usd = tk.Entry( frame_recibir_cantidad, textvariable = string_recibir_usd, state = 'disabled' )
        textbox_recibir_cantidad_usd.insert( 0, '' )
        textbox_recibir_cantidad_usd.grid( row = 2, column = 4, padx = 10 )

        ## variable for radio button
        amount_radio_button = tk.StringVar()
        amount_radio_button.set('cry')

        ## radio button generation
        tk.Radiobutton( frame_recibir_cantidad, text = 'Crypto', variable = amount_radio_button, value = 'cry', command = lambda:habilitar_seleccion( amount_radio_button.get(), textbox_recibir_cantidad_cry, textbox_recibir_cantidad_usd ) ).grid( row = 2, column = 1 )
        tk.Radiobutton( frame_recibir_cantidad, text = 'USD', variable = amount_radio_button, value = 'usd', command = lambda:habilitar_seleccion( amount_radio_button.get(), textbox_recibir_cantidad_cry, textbox_recibir_cantidad_usd ) ). grid( row = 2, column = 3 )

        ## label to indicate how to fill text entry
        label_codigo_recibir = tk.Label( frame_recibir_cantidad, text = "Inserte su Código de Transacción", font = ( 'Helvetica', 8 ) )
        label_codigo_recibir.grid( row = 1, column = 5, padx = 10 )

        ## Text entry for personal code
        textbox_recibir_cantidad_codigo = tk.Entry( frame_recibir_cantidad )
        textbox_recibir_cantidad_codigo.insert( 0, '' )
        textbox_recibir_cantidad_codigo.grid( row = 2, column = 5, padx = 10 )

        ## Combo Box for cryptos
        list_value_recibir = tk.StringVar()
        cripto_list_recibir = Combobox( frame_recibir_cantidad, textvariable = list_value_recibir,
                                    state = 'readonly', height = '6',
                                    justify = 'center', font = ( 'Helvetica', 12 )
                                    )

        ## List of cryptos
        cripto_list_recibir['values'] = monedas
        cripto_list_recibir.grid( row = 2, column = 0, padx = 10 )
        #cripto_list_recibir.bind( '<<ComboboxSelected>>', cripto_selected )

        ## Button to take action
        button_recibir_cantidad = tk.Button( frame_recibir_cantidad, text = 'Recibir Cantidad', command = lambda: recibir_clicked( cripto_list_recibir.get(), string_recibir_cry.get(), string_recibir_usd.get(), textbox_recibir_cantidad_codigo.get() ) )
        button_recibir_cantidad.grid( row = 2, column = 6, padx = 10 )
        
    elif selector == 'Transferir Monto':
        ## If 'Transferir Monto' selected, actuators are shown

        ## Control Label to check if selection is correct
        #labelTest.configure( text = "Transferir Monto" )

        ## Text entry for amount crypto
        string_transferir_cry = tk.StringVar(  frame_transferir_monto )
        textbox_transferir_monto_cry = tk.Entry( frame_transferir_monto, textvariable = string_transferir_cry, state = 'normal' )
        textbox_transferir_monto_cry.insert( 0, '' )
        textbox_transferir_monto_cry.grid( row = 4, column = 2, padx = 10 )

        ## Text entry for amount usd
        string_transferir_usd = tk.StringVar(  frame_transferir_monto )
        textbox_transferir_monto_usd = tk.Entry( frame_transferir_monto, textvariable = string_transferir_usd, state = 'disable' )
        textbox_transferir_monto_usd.insert( 0, '' )
        textbox_transferir_monto_usd.grid( row = 4, column = 4, padx = 10 )

        ## variable for radio button
        amount_radio_button_transferir = tk.StringVar()
        amount_radio_button_transferir.set('cry')

        ## radio button generation
        tk.Radiobutton( frame_transferir_monto, text = 'Crypto', variable = amount_radio_button_transferir, value = 'cry', command = lambda:habilitar_seleccion( amount_radio_button_transferir.get(), textbox_transferir_monto_cry, textbox_transferir_monto_usd ) ).grid( row = 4, column = 1 )
        tk.Radiobutton( frame_transferir_monto, text = 'USD', variable = amount_radio_button_transferir, value = 'usd', command = lambda:habilitar_seleccion( amount_radio_button_transferir.get(), textbox_transferir_monto_cry, textbox_transferir_monto_usd ) ). grid( row = 4, column = 3 )
        
        ## label to indicate how to fill text entry
        label_codigo_transferir = tk.Label( frame_transferir_monto, text = "Inserte el Código de Transacción del Comprador", font = ( 'Helvetica', 8 ) )
        label_codigo_transferir.grid( row = 3, column = 5, padx = 10 )
        #labelTest.configure( text = "Arranque" )

        ## Text entry for personal code
        textbox_transferir_monto_codigo = tk.Entry( frame_transferir_monto )
        textbox_transferir_monto_codigo.insert( 0, '' )
        textbox_transferir_monto_codigo.grid( row = 4, column = 5, padx = 10 )

        ## Combo Box for cryptos
        list_value_transferir = tk.StringVar()
        cripto_list_transferir = Combobox( frame_transferir_monto, textvariable = list_value_transferir,
                                    state = 'readonly', height = '6',
                                    justify = 'center', font = ( 'Helvetica', 12 )
                                    )

        ## List of cryptos
        cripto_list_transferir['values'] = monedas
        cripto_list_transferir.grid( row = 4, column = 0, padx = 10 )

        ## Button to take action
        button = tk.Button( frame_transferir_monto, text = 'Transferir', command = lambda: transferir_clicked( cripto_list_transferir.get(), string_transferir_cry.get(), string_transferir_usd.get(), textbox_transferir_monto_codigo.get() ) )
        button.grid( row = 4, column = 6, padx = 10 )

    elif selector == 'Mostrar Balance de Moneda':
        ## If 'Mostrar Balance de Moneda' selected, actuators are shown

        #labelTest.configure( text = "Balance de Moneda" )

        ## Button to take action
        button = tk.Button( frame_mostrar_balance_moneda, text = 'Mostrar Balance de Moneda', command = lambda: consultar_crypto_clicked( cripto_list_consultar.get(), label_balance_moneda ) )
        button.grid( row = 5, column = 1, padx = 10 )

        ## Label to show crypto balance
        label_balance_moneda = tk.Label( frame_mostrar_balance_moneda, text = "", font = ( 'Helvetica', 12 ), fg = 'black' )
        label_balance_moneda.grid( row = 5, column = 2, padx = 10 )

        ## Combo Box for cryptos
        list_value_consultar = tk.StringVar()
        cripto_list_consultar = Combobox( frame_mostrar_balance_moneda, textvariable = list_value_consultar,
                                    state = 'readonly', height = '6',
                                    justify = 'center', font = ( 'Helvetica', 12 )
                                    )

        ## List of cryptos
        cripto_list_consultar['values'] = monedas
        cripto_list_consultar.grid( row = 5, column = 0, padx = 10 )

    elif selector == 'Mostrar Balance General':
        ## If 'Mostrar Balance General' selected, actuators are shown

        #labelTest.configure( text = "Balance General" )

        ## Button to take action
        button_balance_general = tk.Button( frame_mostrar_balance_general, text = 'Mostrar Balance General', command = show_balance_general )
        button_balance_general.grid( row = 6, column = 0, padx = 10 )

        ## Label for Balance Gral
        #label_balance_general = tk.Label( frame_mostrar_balance_general, text = "", font = ( 'Helvetica', 12 ), fg = 'black' )
        #label_balance_general.grid( row = 6, column = 1, padx = 10 )

    elif selector == 'Mostrar Histórico de Transacciones':
        ## If 'Mostrar Histórico de Transacciones' selected, actuators are shown

        #labelTest.configure( text = "Histórico" )

        ## Button to take action
        button = tk.Button( frame_mostrar_historico, text = 'Generar Histórico de Transacciones', command = create_archivo_transacciones )
        button.grid( row = 7, column = 0, padx = 10 )

        ## Label for Histórico
        #label_historico = tk.Label( frame_mostrar_historico, text = "", font = ( 'Helvetica', 12 ), fg = 'black' )
        #label_historico.grid( row = 7, column = 1, padx = 10 )

    elif selector == 'Salir':
        ## If 'Salir' selected, quit mainwindow
        rootWidget.quit()

## when 'Recibir Cantidad' button is pressed, 'recibir_clicked' is called
def recibir_clicked( crypto, cantidad_cry, cantidad_usd, codigo ):
    
    if crypto == '':
        ## generating the message and message window to notify user if selection is empty
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        if cantidad_cry == '' and cantidad_usd == '':
            ## generating the message and message window to notify user if amount is empty
            msg = f'You have to enter the amount of crypto you want to receive'
            showinfo( title = 'Stop!', message = msg )
        else:
            if codigo == '':
                ## generating the message and message window to notify user if code is empty
                msg = f'You have to enter the code for completing transaction'
                showinfo( title = 'Stop!', message = msg )
            elif codigo != codigo_personal:
                ## generating the message and message window to notify user if code is incorrect
                msg = f'You have to enter the correct code for operating'
                showinfo( title = 'Stop!', message = msg )
            else:
                ## checking if amount is in USD or crypto
                if cantidad_cry == '':
                    ## check if input is numerical
                    try:
                        cantidad_usd = float( cantidad_usd )
                        error_found = 0
                        cantidad = str( cantidad_usd  / float( monedas_values[ crypto ] ) )
                        
                    except:
                        ## generating the message and message window to notify user if input is incorrect
                        msg = f'You have to enter a numerical input'
                        showinfo( title = 'Stop!', message = msg )
                        error_found = 1                    
                    
                elif cantidad_usd == '':
                    ## check if input is numerical
                    try:
                        cantidad_cry = float( cantidad_cry )
                        error_found = 0
                        cantidad = str( cantidad_cry )
                    except:
                        ## generating the message and message window to notify user if input is incorrect
                        msg = f'You have to enter a numerical input'
                        showinfo( title = 'Stop!', message = msg )
                        error_found = 1

                if error_found == 0:
                    ## no error was found in the amount input
                    global contador_transacciones
                    monedas_billetera[ crypto ] = monedas_billetera[ crypto ] + float(cantidad)
                    ## generating record on file
                    transacciones = open( archivo_transacciones, 'a' )
                    transacciones.write( '\n' + str( contador_transacciones ) + '\t' + str( datetime.datetime.now() ) + '\t' + crypto + '\t' + '+' + cantidad + '\t' + '-' + str( monedas_values[ crypto ] * float( cantidad ) ) )
                    transacciones.close()
                    contador_transacciones = contador_transacciones + 1
                    ## generating the message and message window to notify user
                    msg = f'Now you have { monedas_billetera[ crypto ] } of { crypto } crypto!'
                    showinfo( title = 'Stop!', message = msg )

## when 'Transferir' button is pressed, 'transferir_clicked' is called    
def transferir_clicked( crypto, cantidad_cry, cantidad_usd, codigo ):
    
    if crypto == '':
        ## generating the message and message window to notify user if selection is empty
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        if cantidad_cry == '' and cantidad_usd == '':
            ## generating the message and message window to notify user if amount is empty
            msg = f'You have to enter the amount of crypto you want to tranfer'
            showinfo( title = 'Stop!', message = msg )
        else:
            if codigo == '':
                ## generating the message and message window to notify user if code is empty
                msg = f'You have to enter the code for completing transaction'
                showinfo( title = 'Stop!', message = msg )
            elif codigo in codigos_para_transaccion:
                ## checking if amount is in USD or crypto
                if cantidad_cry == '':
                    ## check if input is numerical
                    try:
                        cantidad_usd = float( cantidad_usd )
                        error_found = 0
                        cantidad = str( cantidad_usd / float( monedas_values[ crypto ] ) )
                    except:
                        ## generating the message and message window to notify user if input is incorrect
                        msg = f'You have to enter a numerical input'
                        showinfo( title = 'Stop!', message = msg )
                        error_found = 1

                elif cantidad_usd == '':
                    ## check if input is numerical
                    try:
                        cantidad_cry = float( cantidad_cry )
                        error_found = 0
                        cantidad = str( cantidad_cry )
                    except:
                        ## generating the message and message window to notify user if input is incorrect
                        msg = f'You have to enter a numerical input'
                        showinfo( title = 'Stop!', message = msg )
                        error_found = 1
                
                if error_found == 0:
                    ## no error was found in the amount input
                    new_cantidad = monedas_billetera[ crypto ] - float( cantidad )
                    if new_cantidad < 0:
                        ## generating the message and message window to notify user if amount is bigger than the one that the user has
                        msg = f'You cannot tranfer that amount because you do not have that amount'
                        showinfo( title = 'Stop!', message = msg )
                    else:
                        monedas_billetera[ crypto ] = new_cantidad
                        global contador_transacciones
                        ## generating record on file
                        transacciones = open( archivo_transacciones, 'a' )
                        transacciones.write( '\n' + str( contador_transacciones ) + '\t' + str( datetime.datetime.now() ) + '\t' + crypto + '\t' + '-' + cantidad + '\t' + '-' + str( monedas_values[ crypto ] * float( cantidad ) ) )
                        transacciones.close()
                        contador_transacciones = contador_transacciones + 1
                        ## generating the message and message window to notify user
                        msg = f'Now you have { new_cantidad } of { crypto } crypto!'
                        showinfo( title = 'Stop!', message = msg )
            else:
                ## generating the message and message window to notify user if code is incorrect
                msg = f'The code is not authorized for operating'
                showinfo( title = 'Stop!', message = msg )

## when 'Mostrar Balance de Moneda' button is pressed, 'consultar_crypto_clicked' is called
def consultar_crypto_clicked( crypto, label_balance_moneda ):
    if crypto == '':
        ## control for crypto selection
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        ## printing Balance of selected crypto in Label
        cantidad_cripto = str( round( monedas_billetera[ crypto ], 5 ) )
        cantidad_usd = str( round( monedas_billetera[ crypto ] * monedas_values[ crypto ], 5 ) )
        label_balance_moneda.configure( text = 'You have ' + cantidad_cripto + ' of ' + crypto + '. That is USD ' + cantidad_usd )

## when 'Mostrar Balance General' button is pressed, 'show_balance_general' is called
def show_balance_general(  ):

    ## generating new window to show the records
    balance_general = tk.Toplevel()
    monedas_local = monedas_dict.keys()
    contador_filas_label = 0
    contador_columnas_label = 0
    
    ## generating each record with amount over 0 (so window size is smaller than it will be with all records)
    for cripto_local in monedas_local:
        if monedas_billetera[ cripto_local ] > 0:
            registro_cripto = str( contador_filas_label + 1 ) + '\t' + str( cripto_local ) + '\t' + str( monedas_billetera[ cripto_local ] ) + '\tUSD ' + str( monedas_billetera[ cripto_local ] * monedas_values[ cripto_local ] )
            label = tk.Label( balance_general, text = registro_cripto, font = ( 'Helvetica', 12 ), fg = 'black' )
            label.grid( row = contador_filas_label, column = contador_columnas_label )
            contador_filas_label = contador_filas_label + 1
    
    ## button to generate full file
    button_generar_balance_general = tk.Button ( balance_general, text = 'Generar Archivo con Balance General', command = generar_balance_general )
    button_generar_balance_general.grid( row = contador_filas_label, column = 0 )

    #balance_general.protocol( 'WM_DELETE_WINDOW', habilitar_show_balance_general( widget ) )

## when 'Generar Archivo con Balance General' button is pressed, 'generar_balance_general' is called
def generar_balance_general(  ):

    monedas_local = monedas_dict.keys()
    archivo_balance_general = 'Balance General de Criptomonedas.txt'
    path = ''

    ## deleting, if exists, file of 'Balance General de Criptomonedas'
    if os.path.exists( 'Balance General de Criptomonedas.txt' ):
        os.remove( 'Balance General de Criptomonedas.txt' )

    ## generating new file for Balance General de Criptomonedas
    balance_gral_local = open( archivo_balance_general, 'a' )
    contador_balance = 0
    
    ## generating each record
    for cripto_local in monedas_local:
        registro_cripto_general = str( contador_balance + 1 ) + '\t' + str( cripto_local ) + '\t' + str( monedas_billetera[ cripto_local ] ) + '\tUSD ' + str( monedas_billetera[ cripto_local ] * monedas_values[ cripto_local ] )
        balance_gral_local.write( registro_cripto_general + '\n' )
        contador_balance = contador_balance + 1

    balance_gral_local.close()
    ## generating the message and message window to notify user
    msg = f'The file was generated and downloaded succesfully!'
    showinfo( title = 'Success!', message = msg )

## when radio button selection changes, 'habilitar_seleccion' is called
def habilitar_seleccion( valor_radio, textbox_cry, textbox_usd ):

    if valor_radio == 'cry':
        ## if crypto radio button is selected, text entry for crypto is enable and text entry for USD is empty and then disable
        textbox_cry.config( state = 'normal' )
        textbox_usd.delete( 0, 'end' )
        textbox_usd.config( state = 'disable' )

    elif valor_radio == 'usd':
        ## if USD radio button is selected, text entry for USD is enable and text entry for crypto is empty and then disable
        textbox_cry.delete( 0, 'end' )
        textbox_cry.config( state = 'disable' )
        textbox_usd.config( state = 'normal' )

## when 'Generar Histórico de Transacciones' button is pressed, 'create_archivo_transacciones' is called
def create_archivo_transacciones(  ):

    ## open and edit the transaction's file
    transacciones = open( archivo_transacciones, 'a' )
    transacciones.write( '\n' + 'This is the end of the file. This are all the transactions made till' + str( datetime.datetime.now() ) )
    transacciones.close()

    ## generating the message and message window to notify user
    msg = f'The file was generated and downloaded succesfully!'
    showinfo( title = 'Success!', message = msg )

## Creating the main window of the desktop app
## generating the object
mainWindow = tk.Tk()
## giving size to main window
mainWindow.geometry( '1000x400' )
## giving title to main window
mainWindow.title( 'Prueba Main Window Proyecto Final' )

## Creating and placing the different frames for each option

frame_recibir_cantidad = tk.Frame( mainWindow )
frame_recibir_cantidad.place( x = 0, y = 50, width = 1000, height = 50 )

frame_transferir_monto = tk.Frame( mainWindow )
frame_transferir_monto.place( x = 0, y = 150, width = 1000, height = 50 )

frame_mostrar_balance_moneda = tk.Frame( mainWindow )
frame_mostrar_balance_moneda.place( x = 0, y = 250, width = 800, height = 50 )

frame_mostrar_balance_general = tk.Frame( mainWindow )
frame_mostrar_balance_general.place( x = 0, y = 300, width = 800, height = 50 )

frame_mostrar_historico = tk.Frame( mainWindow )
frame_mostrar_historico.place( x = 0, y = 350, width = 800, height = 50 )

## array with selectable options of dropdown menu
optionList = ( 'Recibir Cantidad', 'Transferir Monto', 'Mostrar Balance de Moneda', 'Mostrar Balance General', 'Mostrar Histórico de Transacciones', 'Salir' )
## crating default value
menuname = tk.StringVar()
menuname.set( 'Menú Principal' )
## generation of dropdown menu
optionmenu = tk.OptionMenu( mainWindow, menuname, *optionList, command = lambda x: desplegar_frame_seleccionado( x, mainWindow ) )
## positioning of dropdown menu
optionmenu.grid( row = 0, column = 0 )

## test label to check if selection is OK
#labelTest = tk.Label( text = "", font = ( 'Helvetica', 12 ), fg = 'red' )
#labelTest.grid( row = 0, column = 2 )
#labelTest.configure( text = "Arranque" )

## Personal transaction code
codigo_personal = '18101994'
## Possible transaction codes
codigos_para_transaccion = ( '25051998', '18052004', '08041964', '19061970' )

## global variables associated to crypto managment
monedas = []
monedas_billetera = {}
monedas_dict = {}
monedas_values = {}
crypto_selected = ''
crypto_cantidad_total = 0
archivo_transacciones = 'Transacciones.txt' 
contador_transacciones = 0

## API 

COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': COINMARKET_API_KEY
}

data = requests.get( "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers = headers ).json()

## saveing API results to global variables

for cripto in data[ "data" ]:
    monedas_dict[ cripto[ "symbol" ] ]=cripto[ "name" ]
    monedas_billetera[ cripto[ 'symbol' ] ] = 0
    monedas_values[ cripto[ 'symbol' ] ] = cripto[ 'quote' ][ 'USD' ][ 'price' ]
    monedas.append( cripto[ "symbol" ] )

## looping for GUI
mainWindow.mainloop()