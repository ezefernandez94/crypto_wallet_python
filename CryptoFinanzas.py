from typing import Collection
import requests
import datetime
from datetime import datetime
import xlsxwriter
import traceback
import time
import os
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.messagebox import showinfo
from tkinter.filedialog import asksaveasfile, askdirectory
from tkinter import Frame, Variable, Scrollbar, Text
from tkinter.constants import HORIZONTAL, S, VERTICAL, RIGHT, LEFT, BOTH, END, Y
import sqlite3
from sqlite3 import Error
import pathlib
from pathlib import Path



class TextExtension(Frame):
    """Extends Frame.  Intended as a container for a Text field.  Better related data handling
    and has Y scrollbar."""

    def __init__(self, master, textvariable=None, *args, **kwargs):

        super(TextExtension, self).__init__(master)
        # Init GUI

        self._y_scrollbar = Scrollbar(self, orient=VERTICAL)

        self._text_widget = Text(self, bg='black', fg='green' ,yscrollcommand=self._y_scrollbar.set, *args, **kwargs)
        self._text_widget.pack(side=LEFT, fill=BOTH, expand=1)

        self._y_scrollbar.config(command=self._text_widget.yview)
        self._y_scrollbar.pack(side=RIGHT, fill=Y)

        if textvariable is not None:
            if not (isinstance(textvariable, Variable)):
                raise TypeError("tkinter.Variable type expected, " + str(type(textvariable)) + " given.".format(type(textvariable)))
            self._text_variable = textvariable
            self.var_modified()
            self._text_trace = self._text_widget.bind('<<Modified>>', self.text_modified)
            self._var_trace = textvariable.trace("w", self.var_modified)

    def text_modified(self, *args):
            if self._text_variable is not None:
                self._text_variable.trace_vdelete("w", self._var_trace)
                self._text_variable.set(self._text_widget.get(1.0, END))
                self._var_trace = self._text_variable.trace("w", self.var_modified)
                self._text_widget.edit_modified(False)

    def var_modified(self, *args):
        self.set_text(self._text_variable.get())
        self._text_widget.edit_modified(False)

    def unhook(self):
        if self._text_variable is not None:
            self._text_variable.trace_vdelete("w", self._var_trace)

    def clear(self):
        self._text_widget.delete(1.0, END)

    def set_text(self, _value):
        self.clear()
        if (_value is not None):
            self._text_widget.insert(END, _value)

    def insert_text(self, _value):
        if (_value is not None):
            self._text_widget.insert(END, _value)

    def clear_text(self):
        self.clear()

#########################################
##### Creating DataBase Connections #####
#########################################
#temp_path = os.path.dirname(os.path.abspath(__file__))


script_path = os.path.join(os.environ['USERPROFILE'],'Desktop\Archivos Crypto')
Path(script_path).mkdir(parents=True, exist_ok=True)
cur = None

try:
    con = sqlite3.connect( script_path + '\crypto.db' )
    cur = con.cursor()
except Error as e:
    ## generating the message and message window to notify user if amount is empty
    msg = f'Error! Cannot create the database connection.'
    msg += e
    showinfo( title = 'Stop!', message = msg )
else:
    try:
        cur.execute( ''' CREATE TABLE IF NOT EXISTS cryptos (
            id integer PRIMARY KEY AUTOINCREMENT,
            crypto_code text NOT NULL,
            amount double NOT NULL,
            last_date datetime NOT NULL
        ) ''' )
        cur.execute( ''' CREATE TABLE IF NOT EXISTS transactions_history (
            id integer PRIMARY KEY AUTOINCREMENT,
            crypto_code text NOT NULL,
            crypto_value double NOT NULL,
            amount double NOT NULL,
            precio_pesos double NOT NULL,
            dolar_value double NOT NULL,
            transaction_type text NOT NULL,
            transaction_date datetime NOT NULL
        ) ''' )
        cur.execute( ''' CREATE TABLE IF NOT EXISTS transaction_type(
            id integer PRIMARY KEY AUTOINCREMENT,
            transaction_type text NOT NULL
        )''' )
        cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Buy',) )
        cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Sell',) )
        cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Trade',) )
        cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Stack',) )
        cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Games',) )
        cur.execute( ''' CREATE TABLE IF NOT EXISTS request_history (
            id integer PRIMARY KEY AUTOINCREMENT,
            crypto_code text NOT NULL,
            crypto_value double NOT NULL,
            request_date datetime NOT NULL
        ) ''' )
        cur.execute(''' CREATE TABLE IF NOT EXISTS trading_history (
            id integer PRIMARY KEY AUTOINCREMENT,
            initial_crypto_code text NOT NULL,
            final_crypto_code text NOT NULL,
            initial_crypto_amount double NOT NULL,
            final_crypto_amount double NOT NULL,
            final_crypto_value double NOT NULL,
            convertion_index double NOT NULL,
            trading_date datetime NOT NULL
        ) ''')
        con.commit()
    except Error as e:
        ## generating the message and message window to notify user if amount is empty
        msg = f'Error! Cannot create databases.'
        msg += e
        showinfo( title = 'Stop!', message = msg )



## write excel file
def write_excel_file( filename, data_header, data, tipo_archivo ):
    ## creating the file
    #folder = askdirectory(title='Pick a folder', initialdir=str(Path.home()))
    #new_filename = folder + '/' + tipo_archivo + '.xlsx'
    #print(new_filename)
    excel_file = xlsxwriter.Workbook( filename )
    ## adding a sheet
    excel_sheet = excel_file.add_worksheet( tipo_archivo )
    if tipo_archivo == 'Histórico de Transacciones':
        ##data writting
        for header_item in range(len(data_header)):
            ## cycle for header
            excel_sheet.write( 0, header_item, data_header[header_item] )
            for data_item in range( len( data ) ):
                ##cycle for data
                contador = data_item + 1
                excel_sheet.write( contador, header_item, data[data_item][header_item] )
    elif tipo_archivo == 'Balance General':
        for header_item in range(len(data_header)):
            excel_sheet.write( 0, header_item, data_header[header_item] )
            if header_item != (len( data_header ) - 1):
                for data_item in range( len( data ) ):
                    ##cycle for data
                    contador = data_item + 1
                    excel_sheet.write( contador, header_item, data[data_item][header_item] )
            else:
                for data_item in range( len( data ) ):
                    ##cycle for data
                    new_data = data[data_item][header_item - 1] * monedas_values[ data[data_item][header_item - 2] ] # 2 es cantidad, 1 es codigo
                    contador = data_item + 1
                    excel_sheet.write( contador, header_item, new_data )
    excel_file.close()

## when 'Recibir Cantidad' button is pressed, 'recibir_clicked' is called
def recibir_clicked(  ):
    
    crypto = cripto_list_recibir.get()
    if crypto == '':
        ## no code was selected
        ## generating the message and message window to notify user if selection is empty
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    
    cantidad = textbox_recibir_cantidad_cry.get()
    cantidad = cantidad.replace(',','.')

    valor_pesos = textbox_recibir_cantidad_pesos.get()
    valor_pesos = valor_pesos.replace(',','.')

    try:
        cantidad = float( cantidad )
    except Exception as e:
        print(traceback.format_exc())
        ## no numerical input for crypto amount
        ## generating the message and message window to notify user if amount is empty
        msg = f'You have to enter a numerical amount for crypto you will receive'
        showinfo( title = 'Stop!', message = msg )
    else:
        try:
            valor_pesos = float( valor_pesos )
        except Exception as e:
            print(traceback.format_exc())
            ## no numerical input for pesos amount
            ## generating the message and message window to notify user if amount is empty
            msg = f'You have to enter a numerical amount for $$ you paid'
            showinfo( title = 'Stop!', message = msg )
            return
        else:
            if cantidad == '':
                ## no input for crypto amount
                ## generating the message and message window to notify user if amount is empty
                msg = f'You have to enter the amount of crypto you will receive'
                showinfo( title = 'Stop!', message = msg )
            if valor_pesos == '':
                ## no input for $$ amount
                ## generating the message and message window to notify user if input is incorrect
                msg = f'You have to enter a numerical input in "Cantidad Pesos($)" field. If you do not buy those cryptos then just enter 0.'
                showinfo( title = 'Stop!', message = msg )
                                
            if variable_check_old_tranfer.get() == 1:
                ## checked
                if textbox_recibir_valor_usd.get() == '':
                    ## no input for dolar blue value
                    ## generating the message and message window to notify user if input is incorrect
                    msg = f'You have to enter an input for dolar value'
                    showinfo( title = 'Stop!', message = msg )
                if textbox_recibir_date.get() == '':
                    ## generating the message and message window to notify user if input is incorrect
                    msg = f'You have to enter an input for tranfer datetime'
                    showinfo( title = 'Stop!', message = msg )
                    #return
                valor_usd_viejo = textbox_recibir_valor_usd.get()
                valor_usd_viejo = valor_usd_viejo.replace(',','.')
                try:
                    valor_usd_viejo = float( valor_usd_viejo )
                except Exception as e:
                    print(traceback.format_exc())
                    ## input for dolar blue value is not a number
                    ## generating the message and message window to notify user if input is incorrect
                    msg = f'You have to enter a numerical input for dolar value'
                    showinfo( title = 'Stop!', message = msg )
                    return
                else:
                    try:
                        new_date = datetime.strptime(textbox_recibir_date.get(), '%Y-%m-%d')
                    except Exception as e:
                        txt_edit.insert_text( traceback.format_exc() )
                        msg = f"Incorrect data format, should be YYYY-MM-DD"
                        showinfo( title = 'Stop!', message = msg )
                    else:
                        cur.execute('SELECT amount, last_date FROM cryptos WHERE crypto_code = ?', (crypto,) )
                        rows = cur.fetchall()
                        if len(rows) == 0:
                            ## There is no reg for that crypto
                            cur.execute( 'INSERT INTO cryptos ( "crypto_code", "amount", "last_date" ) VALUES ( ?, ?, ? )', ( crypto, cantidad, new_date ) )
                            cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "precio_pesos", "dolar_value", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], cantidad, valor_pesos , valor_usd_viejo, 1, new_date ) )
                            con.commit()

                            ## generating the message and message window to notify user
                            msg = f'Now you have { cantidad } of { crypto } crypto!'
                            #showinfo( title = 'Stop!', message = msg )
                            txt_edit.insert_text( msg )
                            txt_edit.insert_text("\n ----------------------------------------------------------\n")
                        else:
                            new_value = float(rows[0][0]) + cantidad
                            cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, new_date, crypto ) )
                            cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "precio_pesos", "dolar_value", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], cantidad, valor_pesos , valor_usd_viejo, 1, new_date ) )
                            con.commit()
                        
                            ## generating the message and message window to notify user
                            msg = f'Now you have { new_value } of { crypto } crypto!'
                            #showinfo( title = 'Stop!', message = msg )
                            txt_edit.insert_text( msg )
                            txt_edit.insert_text("\n ----------------------------------------------------------\n")
            else:
                cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (crypto,) )
                rows = cur.fetchall()
                if len(rows) == 0:
                    ## There is no reg for that crypto
                    cur.execute( 'INSERT INTO cryptos ( "crypto_code", "amount", "last_date" ) VALUES ( ?, ?, ? )', ( crypto, cantidad, datetime.now() ) )
                    #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "dolar_value", "transaction_date" ) VALUES ( ?, ?, ?, ? )', ( crypto, cantidad, valor_usd, datetime.now() ) )
                    cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "precio_pesos", "dolar_value", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], cantidad, valor_pesos , valor_usd, 1, datetime.now() ) )
                    con.commit()

                    ## generating the message and message window to notify user
                    msg = f'Now you have { cantidad } of { crypto } crypto!'
                    #showinfo( title = 'Stop!', message = msg )
                    txt_edit.insert_text( msg )
                    txt_edit.insert_text("\n ----------------------------------------------------------\n")
                else:
                    new_value = rows[0][0] + cantidad
                    cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, datetime.now(), crypto ) )
                    #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "dolar_value", "transaction_date" ) VALUES ( ?, ?, ?, ? )', ( crypto, cantidad, valor_usd, datetime.now() ) )
                    cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "precio_pesos", "dolar_value", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], cantidad, valor_pesos , valor_usd, 1, datetime.now() ) )
                    con.commit()
                
                    ## generating the message and message window to notify user
                    msg = f'Now you have { new_value } of { crypto } crypto!'
                    #showinfo( title = 'Stop!', message = msg )
                    txt_edit.insert_text( msg )
                    txt_edit.insert_text("\n ----------------------------------------------------------\n")

## when 'Transferir' button is pressed, 'transferir_clicked' is called    
def transferir_clicked():

    crypto = cripto_list_transferir.get()
    cantidad_cry = string_transferir_cry.get()
    cantidad_cry = cantidad_cry.replace(',', '.')

    valor_pesos = textbox_transferir_cantidad_pesos.get()
    valor_pesos = valor_pesos.replace(',','.')

    if crypto == '':
        ## generating the message and message window to notify user if selection is empty
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    if cantidad_cry == '':
        ## generating the message and message window to notify user if amount is empty
        msg = f'You have to enter the amount of crypto you want to tranfer'
        showinfo( title = 'Stop!', message = msg )
    ## check if input is numerical
    try:
        cantidad_cry = float( cantidad_cry )
    except:
        ## generating the message and message window to notify user if input is incorrect
        msg = f'You have to enter a numerical input'
        showinfo( title = 'Stop!', message = msg )
    else:
        global cur, con
        ## no error was found in the amount input
        cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (crypto,) )
        rows = cur.fetchall()
        if len(rows) == 0:
            ## There is no crypto to tranfer
            msg = f'You cannot tranfer that amount because you do not have that amount'
            showinfo( title = 'Stop!', message = msg )
        else:
            new_value = rows[0][0] - cantidad_cry
            if new_value < 0:
                ## There is not enough crypto to tranfer
                msg = f'You cannot tranfer that amount because you do not have that amount'
                showinfo( title = 'Stop!', message = msg )
            else:
                cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, datetime.now(), crypto ) )
                #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "transaction_date" ) VALUES ( ?, ?, ? )', ( crypto, -( cantidad_cry ), datetime.now() ) )
                cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "precio_pesos", "dolar_value", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], -( cantidad_cry ), valor_pesos, valor_usd, 2, datetime.now() ) )
                con.commit()
                ## generating the message and message window to notify user
                msg = f'Now you have { new_value } of { crypto } crypto!'
                txt_edit.insert_text( msg )
                txt_edit.insert_text("\n ----------------------------------------------------------\n")

## when 'Mostrar Balance de Moneda' button is pressed, 'consultar_crypto_clicked' is called
def consultar_crypto_clicked( crypto ):
    if crypto == '':
        ## control for crypto selection
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        global cur
        cur.execute( 'SELECT * FROM cryptos WHERE crypto_code = ?', (crypto,) )
        rows = cur.fetchall()
        ## printing Balance of selected crypto in Label
        cantidad_cripto = str( round( rows[0][2], 5 ) )
        cantidad_usd = str( round( rows[0][2] * monedas_values[ crypto ], 5 ) )
        txt_edit.clear_text()
        txt_edit.insert_text( 'You have ' + cantidad_cripto + ' of ' + crypto + '. That is USD ' + cantidad_usd )
        txt_edit.insert_text("\n ------------------------------ Fin de respuesta ----------------------------\n")

## when 'Mostrar Balance General' button is pressed, 'show_balance_general' is called
def show_balance_general(  ):

    global cur
    cur.execute( 'SELECT * FROM cryptos' )
    rows = cur.fetchall()
    contador = 0
    txt_edit.clear_text()
    for row in rows:
        cantidad_cripto = str( round( rows[contador][2], 5 ) )
        cantidad_usd = str( round( rows[contador][2] * monedas_values[ rows[contador][1] ], 5 ) )
        txt_edit.insert_text( 'You have ' + cantidad_cripto + ' of ' + rows[contador][1] + '. That is USD ' + cantidad_usd )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
        contador += 1

## when 'Generar Archivo con Balance General' button is pressed, 'generar_balance_general' is called
def generar_balance_general(  ):

    global cur, script_path
    cur.execute( 'SELECT * FROM cryptos' )
    rows = cur.fetchall()
    print(rows)
    archivo_balance_general = str( script_path ) + '\Balance General de Criptomonedas.xlsx'
    header = ['# Registro', 'Crypto Code', 'Cantidad Total', 'Valor Actual']
    
    ## deleting, if exists, file of 'Balance General de Criptomonedas'
    if os.path.exists( archivo_balance_general ):
        os.remove( archivo_balance_general )

    ## generating new file for Balance General de Criptomonedas
    #balance_gral_local = open( archivo_balance_general, 'a' )
    #contador = 0
    ## generating each record
    #for row in rows:
    #    registro_cripto_general = str( rows[contador][0] ) + '\t' + str( rows[contador][1] ) + '\t' + str( rows[contador][2] ) + '\tUSD ' + str( rows[contador][2] * monedas_values[ rows[contador][1] ] )
    #    balance_gral_local.write( registro_cripto_general + '\n' )
    #    contador += 1

    #balance_gral_local.close()
    try:
        write_excel_file( archivo_balance_general, header, rows, 'Balance General' )
        ## generating the message and message window to notify user
        msg = f'The file was generated and downloaded succesfully!'
        txt_edit.insert_text( msg )
        showinfo( title = 'Success!', message = msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
    except Exception as e:
        txt_edit.insert_text( traceback.format_exc() )

## when 'Generar Histórico de Transacciones' button is pressed, 'create_archivo_transacciones' is called
def create_archivo_transacciones(  ):

    global cur, script_path
    archivo_transacciones = str( script_path ) + '\Histórico_Transacciones.xlsx'
    ## open and edit the transaction's file

    cur.execute( 'SELECT * FROM transactions_history' )
    rows = cur.fetchall()
    header = ['# Transacción', 'Crypto Code', 'Cantidad', 'Valor Dolar para la Fecha', 'Fecha de Transacción']
    ## deleting, if exists, file of 'Balance General de Criptomonedas'
    if os.path.exists( archivo_transacciones ):
        os.remove( archivo_transacciones )

    try:
        write_excel_file( archivo_transacciones, header, rows, 'Histórico de Transacciones' )
        msg = f'The file was generated and downloaded succesfully!'
        txt_edit.insert_text( msg )
        showinfo( title = 'Success!', message = msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
    except Exception as e:
        txt_edit.insert_text( traceback.format_exc() )


## Control of old tranfer checkbox
def change_tranfer_status():
    if variable_check_old_tranfer.get() == 0:
        textbox_recibir_valor_usd.configure( state = 'disable' )
        textbox_recibir_date.configure( state = 'disable' )
    elif variable_check_old_tranfer.get() == 1:
        textbox_recibir_valor_usd.configure( state = 'normal' )
        textbox_recibir_date.configure( state = 'normal' )

## Creating the main window of the desktop app
## generating the object
mainWindow = tk.Tk()
## giving title to main window
mainWindow.title( 'Billetera Crypto' )

# PANEL DE RESPUESTAS
txt_edit = TextExtension( mainWindow )
txt_edit.grid( row = 0, column = 1, rowspan = 5, sticky = "nswe" )

## global variables associated to crypto managment
monedas = []
monedas_values = {}
crypto_selected = ''

## API Dolar Blue

data_dolar = requests.get('https://www.dolarsi.com/api/api.php?type=valoresprincipales').json()
valor_usd = data_dolar[1]['casa']['venta']

## API Cryptos Coinmarketcap

COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': COINMARKET_API_KEY
}

data_crypto = requests.get( "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers = headers ).json()

## saveing API results to global variables

for cripto in data_crypto[ "data" ]:
    monedas_values[ cripto[ 'symbol' ] ] = cripto[ 'quote' ][ 'USD' ][ 'price' ]
    monedas.append( cripto[ "symbol" ] )

#################################################################################################################################
################################################ COMBOBOX PARA INGRESAR CANTIDAD ################################################
#################################################################################################################################

ingresar_crypto = ttk.LabelFrame( mainWindow, text = 'Ingresar Cantidad' )
ingresar_crypto.grid( row = 0, column = 0, sticky = "nswe" )

label = tk.Label( ingresar_crypto, text = 'Crypto Code', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_value_recibir = tk.StringVar()
cripto_list_recibir = Combobox( ingresar_crypto, textvariable = list_value_recibir,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
cripto_list_recibir['values'] = monedas
cripto_list_recibir.grid( row = 1, column = 0, padx = 10 )
#cripto_list_recibir.bind( '<<ComboboxSelected>>', cripto_selected )

label = tk.Label( ingresar_crypto, text = 'Cantidad Crypto:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 2, column = 0 )

## Text entry for amount crypto
string_recibir_cry = tk.StringVar( ingresar_crypto )
textbox_recibir_cantidad_cry = tk.Entry( ingresar_crypto, textvariable = string_recibir_cry, state = 'normal' )
textbox_recibir_cantidad_cry.insert( 0, '' )
textbox_recibir_cantidad_cry.grid( row = 2, column = 1, padx = 10 )

label = tk.Label( ingresar_crypto, text = 'Cantidad Pesos($):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 3, column = 0 )

## Text entry for amount $$
string_recibir_pesos = tk.StringVar( ingresar_crypto )
textbox_recibir_cantidad_pesos = tk.Entry( ingresar_crypto, textvariable = string_recibir_pesos, state = 'normal' )
textbox_recibir_cantidad_pesos.insert( 0, '' )
textbox_recibir_cantidad_pesos.grid( row = 3, column = 1, padx = 10 )

label = tk.Label( ingresar_crypto, text = 'Valor USD (Blue):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 4, column = 0 )

## Text entry for dolar value
string_valor_usd = tk.StringVar( ingresar_crypto )
textbox_recibir_valor_usd = tk.Entry( ingresar_crypto, textvariable = string_valor_usd, state = 'disabled' )
textbox_recibir_valor_usd.insert( 0, '' )
textbox_recibir_valor_usd.grid( row = 4, column = 1, padx = 10 )

label = tk.Label( ingresar_crypto, text = 'Fecha:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 5, column = 0 )

## Text entry for date
string_date = tk.StringVar( ingresar_crypto )
textbox_recibir_date = tk.Entry( ingresar_crypto, textvariable = string_date )
textbox_recibir_date.insert( 0, str( datetime.today().strftime('%Y-%m-%d') ) )
textbox_recibir_date.configure( state = 'disable' )
textbox_recibir_date.grid( row = 5, column = 1, padx = 10 )

## Checkbox old tranfer
variable_check_old_tranfer = tk.IntVar( ingresar_crypto )
check_old_tranfer = tk.Checkbutton( ingresar_crypto, text = 'Tranferencia Vieja', variable = variable_check_old_tranfer, onvalue = 1, offvalue = 0, command = change_tranfer_status )
check_old_tranfer.grid(row = 6, column = 1 , padx = 5, sticky = "ew")

## Button to take action
button_recibir_cantidad = tk.Button( ingresar_crypto, text = 'Ingresar Cantidad', command = recibir_clicked )
button_recibir_cantidad.grid( row = 6, column = 0, padx = 10, pady = 10 )

##################################################################################################################################
################################################ COMBOBOX PARA DESCONTAR CANTIDAD ################################################
##################################################################################################################################

descontar_crypto = ttk.LabelFrame( mainWindow, text = 'Descontar Cantidad' )
descontar_crypto.grid( row = 1, column = 0, sticky = "nswe" )

label = tk.Label( descontar_crypto, text = 'Crypto Code', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

label = tk.Label( descontar_crypto, text = 'Cantidad Crypto:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 2, column = 0 )

## Text entry for amount crypto
string_transferir_cry = tk.StringVar(  descontar_crypto )
textbox_transferir_monto_cry = tk.Entry( descontar_crypto, textvariable = string_transferir_cry, state = 'normal' )
textbox_transferir_monto_cry.insert( 0, '' )
textbox_transferir_monto_cry.grid( row = 2, column = 1, padx = 10 )

## Combo Box for cryptos
list_value_transferir = tk.StringVar()
cripto_list_transferir = Combobox( descontar_crypto, textvariable = list_value_transferir,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
cripto_list_transferir['values'] = monedas
cripto_list_transferir.grid( row = 1, column = 0, padx = 10 )

label = tk.Label( descontar_crypto, text = 'Cantidad Pesos($):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 3, column = 0 )

## Text entry for amount $$
string_transferir_pesos = tk.StringVar( descontar_crypto )
textbox_transferir_cantidad_pesos = tk.Entry( descontar_crypto, textvariable = string_transferir_pesos, state = 'normal' )
textbox_transferir_cantidad_pesos.insert( 0, '' )
textbox_transferir_cantidad_pesos.grid( row = 3, column = 1, padx = 10 )

## Button to take action
button = tk.Button( descontar_crypto, text = 'Transferir', command = transferir_clicked )
button.grid( row = 4, column = 0, padx = 10, pady = 10 )

##########################################################################################################################################
################################################ COMBOBOX PARA MOSTRAR BALANCE INDIVIDUAL ################################################
##########################################################################################################################################

mostrar_balance_individual = ttk.LabelFrame( mainWindow, text = 'Mostrar Balance Individual' )
mostrar_balance_individual.grid( row = 2, column = 0, sticky = "nswe" )

label = tk.Label( mostrar_balance_individual, text = 'Crypto Code', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_value_consultar = tk.StringVar()
cripto_list_consultar = Combobox( mostrar_balance_individual, textvariable = list_value_consultar,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
cripto_list_consultar['values'] = monedas
cripto_list_consultar.grid( row = 1, column = 0, padx = 10 )

## Button to take action
button = tk.Button( mostrar_balance_individual, text = 'Mostrar Balance de Moneda', command = lambda: consultar_crypto_clicked( cripto_list_consultar.get() ) )
button.grid( row = 2, column = 0, padx = 10 )

## Label to show crypto balance
#label_balance_moneda = tk.Label( mostrar_balance_individual, text = "", font = ( 'Helvetica', 12 ), fg = 'black' )
#label_balance_moneda.grid( row = 3, column = 0, padx = 10 )

#######################################################################################################################################
################################################ COMBOBOX PARA MOSTRAR BALANCE GENERAL ################################################
#######################################################################################################################################

mostrar_balance_general = ttk.LabelFrame( mainWindow, text = 'Mostrar Balance General' )
mostrar_balance_general.grid( row = 3, column = 0, sticky = "nswe" )

## Button to take action
button_balance_general = tk.Button( mostrar_balance_general, text = 'Mostrar Balance General', command = show_balance_general )
button_balance_general.grid( row = 0, column = 0, padx = 10 )

## Button to take action
button_balance_general = tk.Button( mostrar_balance_general, text = 'Generar Balance General', command = generar_balance_general )
button_balance_general.grid( row = 1, column = 0, padx = 10 )

##################################################################################################################################################
################################################ COMBOBOX PARA MOSTRAR HISTÓRICO DE TRANSACCIONES ################################################
##################################################################################################################################################

mostrar_historico = ttk.LabelFrame( mainWindow, text = 'Mostrar Histórico' )
mostrar_historico.grid( row = 4, column = 0, sticky = "nswe" )

## Button to take action
button = tk.Button( mostrar_historico, text = 'Generar Histórico de Transacciones', command = create_archivo_transacciones )
button.grid( row = 0, column = 0, padx = 10 )

## looping for GUI
mainWindow.mainloop()