import requests
import datetime
from datetime import date
import xlsxwriter
import traceback
import os
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.messagebox import showinfo
from tkinter import Frame, Variable, Scrollbar, Text
from tkinter.constants import HORIZONTAL, S, VERTICAL, RIGHT, LEFT, BOTH, END, Y
import sqlite3
from sqlite3 import Error
from pathlib import Path

############################
##### Global Variables #####
############################

ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_PATH_CONFIG = os.path.join(os.environ['ALLUSERSPROFILE'],'CryptoManager\Temp')

if not os.path.exists(DEFAULT_PATH_CONFIG):
    os.makedirs(DEFAULT_PATH_CONFIG)

log_file = DEFAULT_PATH_CONFIG + '/crypto_manager.log'
db_file = DEFAULT_PATH_CONFIG + '/crypto.db'

script_path = os.path.join(os.environ['USERPROFILE'],'Desktop\Archivos Crypto')
Path(script_path).mkdir(parents=True, exist_ok=True)

debug = True
first_time = True
max_log_lines = 10000

cur = None
con = None


###################
##### Classes #####
###################

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

def create_database():
    global cur, con

    try:
        con = sqlite3.connect( db_file )
        con.set_trace_callback(print)
        cur = con.cursor()
    except Error as e:
        ## generating the message and message window to notify user if amount is empty
        #msg = f'Error! Cannot create the database connection.'
        #msg += e
        #showinfo( title = 'Stop!', message = msg )
        if debug:
            print('Error al intentar conectar con la base de datos!')
            print(e)
        write_log('Error al intentar conectar con la base de datos!')
        write_log(e)
        msg = f'Error al intentar conectar con la base de datos!'
        showinfo( title = 'Alto!', message = msg )
    else:
        try:
            cur.execute( ''' CREATE TABLE IF NOT EXISTS transaction_type(
                id integer PRIMARY KEY AUTOINCREMENT,
                transaction_type text NOT NULL
            )''' )
            cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Buy',) )
            cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Sell',) )
            cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Trade',) )
            cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Stack',) )
            cur.execute( 'INSERT INTO transaction_type ( "transaction_type" ) VALUES ( ? )', ('Games',) )
            
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
                usd_fee double NOT NULL,
                local_currency_fee double NOT NULL,
                transaction_type integer NOT NULL,
                transaction_date datetime NOT NULL,
                FOREIGN KEY (transaction_type) REFERENCES transaction_type(id)
            ) ''' )

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
                trading_date datetime NOT NULL,
                transaction_id integer NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions_history(id)
            ) ''')

            con.commit()
        except Error as e:
            ## generating the message and message window to notify user if amount is empty
            #msg = f'Error! Cannot create databases.'
            #msg += e
            #showinfo( title = 'Stop!', message = msg )
            if debug:
                print('Error al intentar crear la base de datos!')
                print(e)
            write_log('Error al intentar crear la base de datos!')
            write_log(e)
            msg = f'Error al intentar crear la base de datos!'
            showinfo( title = 'Alto!', message = msg )

###############################
##### Creating Excel File #####
###############################

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

###################################
##### Managing button actions #####
###################################

########################
##### Fully Tested #####
########################

## when 'Recibir Cantidad' button is pressed, 'income_clicked' is called
def income_clicked( crypto, income_crypto_amount, income_usd_value, date ):
    
    local_currency_value = income_local_currency_textbox.get()
    cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (crypto,) )
    rows = cur.fetchall()
    if len(rows) == 0:
        ## There is no reg for that crypto
        cur.execute( 'INSERT INTO cryptos ( "crypto_code", "amount", "last_date" ) VALUES ( ?, ?, ? )', ( crypto, income_crypto_amount, date ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], income_crypto_amount, income_usd_value , local_currency_value, 1, date ) )
        con.commit()

        ## generating the message and message window to notify user
        #msg = f'Now you have { income_crypto_amount } of { crypto } crypto!'
        msg = f'Ahora se tienen { income_crypto_amount } de la crypto { crypto }!'
        #showinfo( title = 'Stop!', message = msg )
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
    else:
        new_value = rows[0][0] + income_crypto_amount
        cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, date, crypto ) )
        #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "local_currency_fee", "transaction_date" ) VALUES ( ?, ?, ?, ? )', ( crypto, cantidad, valor_usd, datetime.now() ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], income_crypto_amount, income_usd_value , local_currency_value, 1, date ) )
        con.commit()
    
        ## generating the message and message window to notify user
        #msg = f'Now you have { new_value } of { crypto } crypto!'
        msg = f'Ahora se tienen { new_value } de la crypto { crypto }!'
        #showinfo( title = 'Stop!', message = msg )
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
    update_crypto_lists()

## when 'Transferir' button is pressed, 'expanditure_clicked' is called
def expanditure_clicked( crypto, expanditure_crypto_amount, income_usd_value, date  ):

    local_currency_value = expanditure_local_currency_textbox.get()
    cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (crypto,) )
    rows = cur.fetchall()
    
    new_value = rows[0][0] - expanditure_crypto_amount
    if new_value < 0:
        ## There is not enough crypto to tranfer
        #msg = f'You cannot tranfer that amount because you do not have that amount'
        msg = f'No se puede realizar la transacción, ya que no cuenta con dicha cantidad'
        showinfo( title = 'Alto!', message = msg )
    else:
        cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, date, crypto ) )
        #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "transaction_date" ) VALUES ( ?, ?, ? )', ( crypto, -( expanditure_crypto_amount ), datetime.now() ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( crypto, monedas_values[ crypto ], -( expanditure_crypto_amount ), income_usd_value, local_currency_value, 2, date ) )
        con.commit()
        ## generating the message and message window to notify user
        msg = f'Now you have { new_value } of { crypto } crypto!'
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
        update_crypto_lists()

## when 'Tradear' button is pressed, 'trading_clicked' is called
def trading_clicked( initial_crypto, initial_crypto_amount, final_crypto, final_crypto_amount, final_crypto_usd_value, date ):
    
    print('¡trading time!')
    #local_currency_value = expanditure_local_currency_textbox.get()
    cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (initial_crypto,) )
    rows = cur.fetchall()

    ## reducing the initial crypto amount
    new_value = rows[0][0] - initial_crypto_amount
    if new_value < 0:
        ## There is not enough crypto to tranfer
        #msg = f'You cannot tranfer that amount because you do not have that amount'
        msg = f'No se puede realizar la transacción, ya que no cuenta con dicha cantidad'
        showinfo( title = 'Alto!', message = msg )
    else:
        cur.execute('UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, date, initial_crypto ) )
        #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "transaction_date" ) VALUES ( ?, ?, ? )', ( crypto, -( expanditure_crypto_amount ), datetime.now() ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( initial_crypto, monedas_values[ initial_crypto ], -( initial_crypto_amount ), 0, 0, 3, date ) )
        con.commit()
        ## generating the message and message window to notify user
        msg = f'Now you have { new_value } of { initial_crypto } crypto!'
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n")
    ## adding incoming crypto
    cur.execute('SELECT amount FROM cryptos WHERE crypto_code = ?', (final_crypto,) )
    rows = cur.fetchall()
    if len(rows) == 0:
        ## There is no reg for that crypto
        cur.execute( 'INSERT INTO cryptos ( "crypto_code", "amount", "last_date" ) VALUES ( ?, ?, ? )', ( final_crypto, final_crypto_amount, date ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( final_crypto, monedas_values[ final_crypto ], final_crypto_amount, 0 , 0, 3, date ) )
        con.commit()

        ## generating the message and message window to notify user
        #msg = f'Now you have { income_crypto_amount } of { crypto } crypto!'
        msg = f'Ahora se tienen { final_crypto_amount } de la crypto { final_crypto }!'
        #showinfo( title = 'Stop!', message = msg )
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n ----------------------------------------------------------\n")
    else:
        new_value = rows[0][0] + final_crypto_amount
        cur.execute( 'UPDATE cryptos SET amount = ?, last_date = ? WHERE crypto_code = ?', ( new_value, date, final_crypto ) )
        #cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "amount", "local_currency_fee", "transaction_date" ) VALUES ( ?, ?, ?, ? )', ( crypto, cantidad, valor_usd, datetime.now() ) )
        cur.execute( 'INSERT INTO transactions_history ( "crypto_code", "crypto_value", "amount", "usd_fee", "local_currency_fee", "transaction_type", "transaction_date" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( final_crypto, monedas_values[ final_crypto ], final_crypto_amount, 0 , 0, 3, date ) )
        con.commit()
    
        ## generating the message and message window to notify user
        #msg = f'Now you have { new_value } of { crypto } crypto!'
        msg = f'Ahora se tienen { new_value } de la crypto { final_crypto }!'
        #showinfo( title = 'Stop!', message = msg )
        txt_edit.insert_text( msg )
        txt_edit.insert_text("\n")
    ## search for last register id in transactions
    cur.execute( 'SELECT id FROM transactions_history ORDER BY id DESC LIMIT 1' )
    row = cur.fetchall()
    print('Last record: ' + str(row[0][0]))
    ## trading register
    cur.execute( 'INSERT INTO trading_history ( "initial_crypto_code", "final_crypto_code", "initial_crypto_amount", "final_crypto_amount", "final_crypto_value", "trading_date", "transaction_id" ) VALUES ( ?, ?, ?, ?, ?, ?, ? )', ( initial_crypto, final_crypto, initial_crypto_amount, final_crypto_amount, final_crypto_usd_value, date, row[0][0] ) )
    con.commit()
    msg = f'Se intercambiaron { initial_crypto_amount } de la crypto { initial_crypto } por { final_crypto_amount } de la crypto { final_crypto }, con un valor inicial de { final_crypto_usd_value }!'
    #showinfo( title = 'Stop!', message = msg )
    txt_edit.insert_text( msg )
    txt_edit.insert_text("\n ----------------------------------------------------------\n")
    update_crypto_lists()

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

    cur.execute( 'SELECT transactions_history.id, crypto_code, crypto_value, amount, usd_fee, local_currency_fee, transaction_type.transaction_type, transaction_date FROM transactions_history LEFT JOIN transaction_type USING(transaction_type)' )
    rows = cur.fetchall()
    print(rows[0])
    header = ['# Transacción', 'Crypto Code', 'Valor al Momento de Transacción', 'Cantidad', 'Valor de Transacción (USD)', 'Valor de Transacción (Moneda Local)', 'Tipo de Transacción', 'Fecha de Transacción']
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

#######################
##### In Progress #####
#######################

## when 'Calcular Rentabilidad Individual' button is pressed, 'individual_profit_clicked' is called
def individual_profit_clicked():
    print('Rentabilidad Individual clicked')
    crypto = cripto_list_other_actions.get()
    if crypto == '':
        ## control for crypto selection
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        global cur
        cur.execute( 'SELECT * FROM transactions_history WHERE crypto_code = ?', (crypto,) )
        rows = cur.fetchall()
        ## printing Balance of selected crypto in Label
        
        #total_pesos = 0
        total_crypto = 0
        total_usds = 0
        total_usds_ficticio = 0
        contador_compras = 0
        
        for i in range(len(rows)):
            total_crypto += rows[i][3]
            if int(rows[i][6]) == 1:
                #es compra
                #total_pesos += rows[i][4]
                total_usds_ficticio += rows[i][2]
                try:
                    total_usds += (rows[i][4] / (rows[i][3] * float(rows[i][5])))
                except:
                    convertion = (rows[i][5]).replace(',','.')
                    total_usds += (rows[i][4] / (rows[i][3] * float(convertion)))
                contador_compras += 1
        
        pago_prom_usds = total_usds/contador_compras
        pago_prom_ficticios = total_usds_ficticio/contador_compras
        
        rentabilidad_ficticia = round(((monedas_values[ crypto ]/pago_prom_ficticios) * 100) - 100, 2)
        rentabilidad_original = round(((monedas_values[ crypto ]/pago_prom_usds) * 100) - 100, 2) 
        
        txt_edit.clear_text()
        txt_edit.insert_text( 'Rentabilidad para ' + crypto + 'es del ' + str(rentabilidad_original) + '% teniendo en cuenta la conversión de $\n' )
        txt_edit.insert_text( 'Rentabilidad para ' + crypto + 'es del ' + str(rentabilidad_ficticia) + '%' + ' sin tener en cuenta la conversión de $' )
        txt_edit.insert_text("\n ------------------------------ Fin de respuesta ----------------------------\n")

## when 'Calcular Rentabilidad Total' button is pressed, 'full_profit_clicked' is called
def full_profit_clicked():
    global cur
    print('Rentabilidad Total clicked')
    txt_edit.clear_text()
    #crypto = cripto_list_other_actions.get()
    #print(monedas_propias)
    for crypto_code in monedas_propias:
        crypto = crypto_code[0]
        #print(crypto)
        cur.execute( 'SELECT * FROM transactions_history WHERE crypto_code = ?', (crypto,) )
        rows = cur.fetchall()
        ## printing Balance of selected crypto in Label
        
        #total_pesos = 0
        total_crypto = 0
        total_usds = 0
        total_usds_ficticio = 0
        contador_compras = 0
        
        for i in range(len(rows)):
            total_crypto += rows[i][3]
            if int(rows[i][6]) == 1:
                #es compra
                #total_pesos += rows[i][4]
                total_usds_ficticio += rows[i][2]
                try:
                    total_usds += (rows[i][4] / (rows[i][3] * float(rows[i][5])))
                except:
                    convertion = (rows[i][5]).replace(',','.')
                    total_usds += (rows[i][4] / (rows[i][3] * float(convertion)))
                contador_compras += 1
        
        pago_prom_usds = total_usds/contador_compras
        pago_prom_ficticios = total_usds_ficticio/contador_compras
        
        rentabilidad_ficticia = round(((monedas_values[ crypto ]/pago_prom_ficticios) * 100) - 100, 2)
        rentabilidad_original = round(((monedas_values[ crypto ]/pago_prom_usds) * 100) - 100, 2) 
        
        #txt_edit.clear_text()
        txt_edit.insert_text( 'Rentabilidad para ' + crypto + ' es del ' + str(rentabilidad_original) + '% teniendo en cuenta la conversión de $\n' )
        txt_edit.insert_text( 'Rentabilidad para ' + crypto + ' es del ' + str(rentabilidad_ficticia) + '%' + ' sin tener en cuenta la conversión de $' )
        txt_edit.insert_text(f"\n ------------------------------ Fin de respuesta para {crypto} ----------------------------\n")

## when 'Calcular Ganancia Individual' button is pressed, 'show_earns_clicked' is called
def show_earns_clicked():

    print('Mostrar Ganancias clicked')
    crypto = cripto_list_other_actions.get()
    if crypto == '':
        ## control for crypto selection
        msg = f'You have to select one crypto-coin'
        showinfo( title = 'Stop!', message = msg )
    else:
        earns_matrix = np.empty((len(monedas_propias), 3)) # crypto_code, precio_compra, precio_actual
        cur.execute( 'SELECT * FROM transactions_history WHERE crypto_code = ?', (crypto,) )
        rows = cur.fetchall()

        txt_edit.clear_text()

        ## printing Balance of selected crypto in Label
        #print(rows)
        total_crypto = 0
        total_value = 0
        total_usds_invertidos = 0
        total_usds_recuperados = 0
        print(len(rows))
        for i in range(len(rows)):
            if int(rows[i][6]) == 3:
                temp_value = float(rows[i][3]) * float(monedas_values[ crypto ])
                total_crypto += rows[i][3]
                temp_earns = temp_value - float(rows[i][4])
                txt_edit.insert_text( 'Se compraron ' + str( rows[i][3] ) + ' tokens de ' + str(crypto) + ', con un valor inicial de USD ' + str( rows[i][4] ) + '. El valor actual para el token es de USD ' + str( monedas_values[ crypto ] ) + ', por lo que el valor en cartera, para esta transacción es de USD ' + str(temp_value) + '. La ganancia total es de USD ' + str(temp_earns) + '.\n' )
                total_value += temp_value
            elif int(rows[i][6]) == 2:
                #es venta
                try:
                    total_usds_recuperados += (rows[i][4] / (float(rows[i][5])))
                except:
                    convertion = (rows[i][5]).replace(',','.')
                    total_usds_recuperados += (rows[i][4] / (float(convertion)))
            elif int(rows[i][6]) == 1:
                print('compra')
        #total_usds_actuales = total_crypto * monedas_values[ crypto ]
        #ganancia_total = total_usds_actuales - total_usds_invertidos - total_usds_recuperados

        
        #txt_edit.insert_text( 'Para ' + crypto + ', se invirtieron ' + str(round(total_usds_invertidos,2)) + ' USD y el valor actual de la cartera es de ' + str(round(total_usds_actuales)) + ' USD. La ganancia total es de ' + str(round(ganancia_total,2)) + 'USD' )
        txt_edit.insert_text("------------------------------ Fin de respuesta ----------------------------\n")

## when 'Calcular Ganancia Total' button is pressed, 'show_total_earns_clicked' is called
def show_total_earns_clicked():

    print('Cálculo de Ganancias Totales')
    #crypto = cripto_list_other_actions.get()
    txt_edit.clear_text()

    cur.execute( 'SELECT * FROM transactions_history' )
    rows = cur.fetchall()
    ## printing Balance of selected crypto in Label
    
    total_usds_invertidos = 0
    total_usd_recuperados = 0
    
    for i in range(len(rows)):

        if rows[i][6] == 1:
            #es compra
            #total_pesos += rows[i][4]
            total_usds_invertidos += rows[i][4]
        if rows[i][6] == 2:
            #es venta
            total_usd_recuperados += rows[i][4]
    
    total_usd_cartera = 0
    
    cur.execute( 'SELECT * FROM cryptos' )
    rows = cur.fetchall()

    for j in range(len(rows)):

        cur.execute( 'SELECT * FROM cryptos' )
        
        total_usd_cartera += rows[j][2] * monedas_values[ rows[j][1] ]
    
    ganancia_total = total_usd_cartera - total_usds_invertidos + total_usd_recuperados
    #cur.execute( 'SELECT * FROM request_history WHERE crypto_code = ? DESC LIMIT 1', (crypto,) )
    
    #txt_edit.clear_text()
    txt_edit.insert_text( 'Se invirtieron USD ' + str( round( total_usds_invertidos, 2 ) ) + ', recuperando en ventas USD ' + str( round( total_usd_recuperados, 2 ) ) + '. El valor actual de la cartera es de USD ' + str( round( total_usd_cartera, 2 ) ) + '. La ganancia total es de USD ' + str( round( ganancia_total, 2 ) ) + '.' )
    txt_edit.insert_text( f"\n ------------------------------ Fin de respuesta ----------------------------\n" )

#############################
##### General Functions #####
#############################

def update_crypto_lists():
    global monedas_propias
    ## erasing previous values
    monedas_propias = []
    ## getting new list values
    cur.execute( 'SELECT crypto_code, amount FROM cryptos' )
    rows_crypto_bougth = cur.fetchall()
    for i in range(len(rows_crypto_bougth)):
        if float(rows_crypto_bougth[i][1]) > 0:
            monedas_propias.append( rows_crypto_bougth[i][0] )
    
    crypto_expanditure_list['values'] = monedas_propias
    initial_crypto_trading_list['values'] = monedas_propias
    cripto_list_other_actions['values'] = monedas_propias

def input_controls( function ):
    
    total_errors = 0
    errors = 'Se encontraron los siguientes errores:\n'
    if function == 0:
        ## income
        if debug:
            print('Controlling variables for incoming function')
        crypto = crypto_income_list.get()
        if crypto == '':
            errors += '- El campo de Código Crypto no puede estar vacío.\n'
            total_errors += 1
        income_crypto_amount = income_amount_textbox.get()
        if income_crypto_amount == '':
            errors += '- El campo de Cantidad Crypto no puede estar vacío.\n'
            total_errors += 1
        else:
            income_crypto_amount = income_crypto_amount.replace(',','.')
            try:
                income_crypto_amount = float( income_crypto_amount )
            except Exception:
                errors += '- El campo de Cantidad Crypto debe contener un valor numérico.\n'
                total_errors += 1
        income_usd_value = income_usd_amount_textbox.get()
        if income_usd_value == '':
            errors += '- El campo de Precio de Compra no puede estar vacío.\n'
            total_errors += 1
        else:
            income_usd_value = income_usd_value.replace(',','.')
            try:
                income_usd_value = float( income_usd_value )
            except Exception:
                errors += '- El campo de Precio de Compra debe contener un valor numérico.\n'
                total_errors += 1
        if incoming_date_textbox.get() == '':
            errors += '- El campo de Fecha no puede estar vacío.\n'
            total_errors += 1
        else:
            try:
                date = datetime.datetime.strptime(incoming_date_textbox.get(), '%Y-%m-%d')
            except:
                errors += '- El campo de Fecha debe contener un valor con el formato YYYY-MM-DD.\n'
                total_errors += 1
        income_local_currency = income_local_currency_textbox.get()
        if income_local_currency != '':
            try:
                income_local_currency = float( income_local_currency.replace(',','.') )
            except Exception:
                errors += '- Si va a completarlo, el campo de Moneda Local debe contener un valor numérico.\n'
                total_errors += 1
        if total_errors == 0:
            income_clicked( crypto, income_crypto_amount, income_usd_value, date )
        else:
            if debug:
                print('Some errors were encounterd')
            write_log('Se encontraron errores al completar los parámetros')
            showinfo( title = 'Alto!', message = errors )
    elif function == 1:
        ## expanditure
        if debug:
            print('Controlling variables for expanditure function')
        crypto = crypto_expanditure_list.get()
        if crypto == '':
            errors += '- El campo de Código Crypto no puede estar vacío.\n'
            total_errors += 1
        expanditure_crypto_amount = expanditure_amount_textbox.get()
        if expanditure_crypto_amount == '':
            errors += '- El campo de Cantidad Crypto no puede estar vacío.\n'
            total_errors += 1
        else:
            expanditure_crypto_amount = expanditure_crypto_amount.replace(',','.')
            try:
                expanditure_crypto_amount = float( expanditure_crypto_amount )
            except Exception:
                errors += '- El campo de Cantidad Crypto debe contener un valor numérico.\n'
                total_errors += 1
        expanditure_usd_value = expanditure_usd_amount_textbox.get()
        if expanditure_usd_value == '':
            errors += '- El campo de Precio de Venta no puede estar vacío.\n'
            total_errors += 1
        else:
            expanditure_usd_value = expanditure_usd_value.replace(',','.')
            try:
                expanditure_usd_value = float( expanditure_usd_value )
            except Exception:
                errors += '- El campo de Precio de Venta debe contener un valor numérico.\n'
                total_errors += 1
        if expanditure_date_textbox.get() == '':
            errors += '- El campo de Fecha no puede estar vacío.\n'
            total_errors += 1
        else:
            try:
                date = datetime.datetime.strptime(expanditure_date_textbox.get(), '%Y-%m-%d')
            except:
                errors += '- El campo de Fecha debe contener un valor con el formato YYYY-MM-DD.\n'
                total_errors += 1
        expanditure_local_currency = expanditure_local_currency_textbox.get()
        if expanditure_local_currency != '':
            try:
                expanditure_local_currency = float( expanditure_local_currency.replace(',','.') )
            except Exception:
                errors += '- Si va a completarlo, el campo de Moneda Local debe contener un valor numérico.\n'
                total_errors += 1
        if total_errors == 0:
            expanditure_clicked( crypto, expanditure_crypto_amount, expanditure_usd_value, date )
        else:
            if debug:
                print('Some errors were encounterd')
            write_log('Se encontraron errores al completar los parámetros')
            showinfo( title = 'Alto!', message = errors )
    elif function == 2:
        ## trading
        if debug:
            print('Controlling variables for trading function')
        initial_crypto = initial_crypto_trading_list.get()
        if initial_crypto == '':
            errors += '- El campo de Código Crypto Inicial no puede estar vacío.\n'
            total_errors += 1
        initial_crypto_amount = initial_amount_textbox.get()
        if initial_crypto_amount == '':
            errors += '- El campo de Cantidad Inicial Crypto no puede estar vacío.\n'
            total_errors += 1
        else:
            initial_crypto_amount = initial_crypto_amount.replace(',','.')
            try:
                initial_crypto_amount = float( initial_crypto_amount )
            except Exception:
                errors += '- El campo de Cantidad Crypto debe contener un valor numérico.\n'
                total_errors += 1
        final_crypto = final_crypto_trading_list.get()
        if final_crypto == '':
            errors += '- El campo de Código Crypto Final no puede estar vacío.\n'
            total_errors += 1
        final_crypto_amount = final_amount_textbox.get()
        if final_crypto_amount == '':
            errors += '- El campo de Cantidad Final Crypto no puede estar vacío.\n'
            total_errors += 1
        else:
            final_crypto_amount = final_crypto_amount.replace(',','.')
            try:
                final_crypto_amount = float( final_crypto_amount )
            except Exception:
                errors += '- El campo de Cantidad Final Crypto debe contener un valor numérico.\n'
                total_errors += 1
        final_crypto_usd_value = final_crypto_value_textbox.get()
        if final_crypto_usd_value == '':
            errors += '- El campo de Precio de Crypto Final no puede estar vacío.\n'
            total_errors += 1
        else:
            final_crypto_usd_value = final_crypto_usd_value.replace(',','.')
            try:
                final_crypto_usd_value = float( final_crypto_usd_value )
            except Exception:
                errors += '- El campo de Precio de Crypto Final debe contener un valor numérico.\n'
                total_errors += 1
        if trading_date_textbox.get() == '':
            errors += '- El campo de Fecha no puede estar vacío.\n'
            total_errors += 1
        else:
            try:
                date = datetime.datetime.strptime(trading_date_textbox.get(), '%Y-%m-%d')
            except:
                errors += '- El campo de Fecha debe contener un valor con el formato YYYY-MM-DD.\n'
                total_errors += 1
        if total_errors == 0:
            trading_clicked( initial_crypto, initial_crypto_amount, final_crypto, final_crypto_amount, final_crypto_usd_value, date )
        else:
            if debug:
                print('Some errors were encounterd')
            write_log('Se encontraron errores al completar los parámetros')
            showinfo( title = 'Alto!', message = errors )
    #msg += 'deben ser completados para continuar.'
    #return True

## Control of old tranfer checkbox
def change_tranfer_status( tipo_transaccion ):
    if tipo_transaccion == 0:
        if variable_check_old_tranfer_departure.get() == 0:
            expanditure_local_currency_textbox.configure( state = 'disable' )
            expanditure_date_textbox.configure( state = 'disable' )
        elif variable_check_old_tranfer_departure.get() == 1:
            expanditure_local_currency_textbox.configure( state = 'normal' )
            expanditure_date_textbox.configure( state = 'normal' )
    elif tipo_transaccion == 1:
        if variable_check_old_tranfer_income.get() == 0:
            income_local_currency_textbox.configure( state = 'disable' )
            incoming_date_textbox.configure( state = 'disable' )
        elif variable_check_old_tranfer_income.get() == 1:
            income_local_currency_textbox.configure( state = 'normal' )
            incoming_date_textbox.configure( state = 'normal' )
    elif tipo_transaccion == 2:
        if variable_check_old_trade.get() == 0:
            final_crypto_value_textbox.configure( state = 'disable' )
            trading_date_textbox.configure( state = 'disable' )
        elif variable_check_old_trade.get() == 1:
            final_crypto_value_textbox.configure( state = 'normal' )
            trading_date_textbox.configure( state = 'normal' )

def write_log( message ):

    global first_time

    if first_time == True:
        try:
            open_file = open( log_file, 'r' )
        except:
            open_file = open( log_file, 'a+' )
        num_lines = 0
        for line in open_file:
            if line != '\n':
                num_lines += 1
        open_file.close()
        if debug:
            print('Número de líneas en archivo log: ' + str(num_lines))
        first_time = False
        if num_lines > max_log_lines:
            start_line = num_lines - max_log_lines
            with open( log_file, 'r' ) as fin:
                data = fin.read().splitlines(True)
            with open( log_file, 'w' ) as fout:
                fout.writelines( data[start_line:] )
                fout.close()
    else:
        open_file = open(log_file, 'a+')
        first_time = False
    log = open( log_file, 'a' )
    string = str( datetime.datetime.now() ) + '\t' + message + '\n'
    log.write( string )
    log.close()

create_database()

## Creating the main window of the desktop app
## generating the object
mainWindow = tk.Tk()
## giving title to main window
mainWindow.title( 'Billetera Crypto' )

# PANEL DE RESPUESTAS
txt_edit = TextExtension( mainWindow )
txt_edit.grid( row = 0, column = 2, rowspan = 5, sticky = "nswe" )

## global variables associated to crypto managment
monedas = []
monedas_values = {}
crypto_selected = ''
monedas_propias = []
## API Dolar Blue

data_dolar = requests.get('https://www.dolarsi.com/api/api.php?type=valoresprincipales').json()
valor_usd = data_dolar[1]['casa']['venta']

## API Cryptos Coinmarketcap

COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': COINMARKET_API_KEY
}

data_crypto = requests.get( "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=500", headers = headers ).json()

## saveing API results to global variables
for cripto in data_crypto[ "data" ]:
    monedas_values[ cripto[ 'symbol' ] ] = cripto[ 'quote' ][ 'USD' ][ 'price' ]
    monedas.append( cripto[ "symbol" ] )

cur.execute( 'SELECT crypto_code, amount FROM cryptos' )
rows_crypto_bougth = cur.fetchall()
for i in range(len(rows_crypto_bougth)):
    if float(rows_crypto_bougth[i][1]) > 0:
        monedas_propias.append( rows_crypto_bougth[i][0] )

#update_crypto_lists()

#################################################################################################################################
################################################ COMBOBOX PARA INGRESAR CANTIDAD ################################################
#################################################################################################################################

crypto_income = ttk.LabelFrame( mainWindow, text = 'Ingresar Cantidad' )
crypto_income.grid( row = 0, column = 0, sticky = "nswe" )

label = tk.Label( crypto_income, text = '*Código Crypto', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_income_string_value = tk.StringVar()
crypto_income_list = Combobox( crypto_income, textvariable = list_income_string_value,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
crypto_income_list['values'] = monedas
crypto_income_list.grid( row = 1, column = 0, padx = 10 )
#crypto_income_list.bind( '<<ComboboxSelected>>', cripto_selected )

label = tk.Label( crypto_income, text = '*Cantidad Crypto:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 2, column = 0 )

## Text entry for amount crypto
income_amount_string_value = tk.StringVar( crypto_income )
income_amount_textbox = tk.Entry( crypto_income, textvariable = income_amount_string_value, state = 'normal' )
income_amount_textbox.insert( 0, '' )
income_amount_textbox.grid( row = 3, column = 0, padx = 10 )

label = tk.Label( crypto_income, text = '*Precio de Compra (USD):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 4, column = 0 )

## Text entry for amount $$
income_usd_amount_string_value = tk.StringVar( crypto_income )
income_usd_amount_textbox = tk.Entry( crypto_income, textvariable = income_usd_amount_string_value, state = 'normal' )
income_usd_amount_textbox.insert( 0, '' )
income_usd_amount_textbox.grid( row = 5, column = 0, padx = 10 )

## Checkbox old tranfer
variable_check_old_tranfer_income = tk.IntVar( crypto_income )
check_old_tranfer_income = tk.Checkbutton( crypto_income, text = 'Tranferencia Vieja', variable = variable_check_old_tranfer_income, onvalue = 1, offvalue = 0, command = lambda: change_tranfer_status( 1 ) )
#check_old_tranfer_income.grid(row = 6, column = 0 , padx = 5, sticky = "ew")

label = tk.Label( crypto_income, text = 'Precio (Moneda Local):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 7, column = 0 )

## Text entry for amount moneda local
income_local_currency_string_value = tk.StringVar( crypto_income )
income_local_currency_textbox = tk.Entry( crypto_income, textvariable = income_local_currency_string_value )
income_local_currency_textbox.insert( 0, '' )
income_local_currency_textbox.grid( row = 8, column = 0, padx = 10 )

label = tk.Label( crypto_income, text = 'Fecha:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 9, column = 0 )

## Text entry for date
income_date_string = tk.StringVar( crypto_income )
incoming_date_textbox = tk.Entry( crypto_income, textvariable = income_date_string )
incoming_date_textbox.insert( 0, str( date.today().strftime('%Y-%m-%d') ) )
#incoming_date_textbox.configure( state = 'disable' )
incoming_date_textbox.grid( row = 10, column = 0, padx = 10 )

## Button to take action
income_button = tk.Button( crypto_income, text = 'Ingresar Cantidad', command = lambda: input_controls( 0 ) )
income_button.grid( row = 11, column = 0, padx = 10, pady = 10 )

##################################################################################################################################
################################################ COMBOBOX PARA DESCONTAR CANTIDAD ################################################
##################################################################################################################################

crypto_expanditure = ttk.LabelFrame( mainWindow, text = 'Descontar Cantidad' )
crypto_expanditure.grid( row = 0, column = 1, sticky = "nswe" )

label = tk.Label( crypto_expanditure, text = '*Código Crypto', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_expanditure_string_value = tk.StringVar()
crypto_expanditure_list = Combobox( crypto_expanditure, textvariable = list_expanditure_string_value,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
crypto_expanditure_list['values'] = monedas_propias
crypto_expanditure_list.grid( row = 1, column = 0, padx = 10 )

label = tk.Label( crypto_expanditure, text = '*Cantidad Crypto:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 2, column = 0 )

## Text entry for amount crypto
expanditure_amount_string_value = tk.StringVar(  crypto_expanditure )
expanditure_amount_textbox = tk.Entry( crypto_expanditure, textvariable = expanditure_amount_string_value, state = 'normal' )
expanditure_amount_textbox.insert( 0, '' )
expanditure_amount_textbox.grid( row = 3, column = 0, padx = 10 )

label = tk.Label( crypto_expanditure, text = '*Precio de Venta (USD):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 4, column = 0 )

## Text entry for amount $$
expanditure_usd_amount_string_value = tk.StringVar( crypto_expanditure )
expanditure_usd_amount_textbox = tk.Entry( crypto_expanditure, textvariable = expanditure_usd_amount_string_value, state = 'normal' )
expanditure_usd_amount_textbox.insert( 0, '' )
expanditure_usd_amount_textbox.grid( row = 5, column = 0, padx = 10 )

## Checkbox old tranfer
variable_check_old_tranfer_departure = tk.IntVar( crypto_expanditure )
check_old_tranfer_departure = tk.Checkbutton( crypto_expanditure, text = 'Tranferencia Vieja', variable = variable_check_old_tranfer_departure, onvalue = 1, offvalue = 0, command = lambda: change_tranfer_status( 0 ) )
#check_old_tranfer_departure.grid(row = 6, column = 0 , padx = 5, sticky = "ew")

label = tk.Label( crypto_expanditure, text = 'Precio (Moneda Local):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 7, column = 0 )

## Text entry for amount moneda local
expanditure_local_currency_string_value = tk.StringVar( crypto_expanditure )
expanditure_local_currency_textbox = tk.Entry( crypto_expanditure, textvariable = expanditure_local_currency_string_value )
expanditure_local_currency_textbox.insert( 0, '' )
expanditure_local_currency_textbox.grid( row = 8, column = 0, padx = 10 )

label = tk.Label( crypto_expanditure, text = 'Fecha:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 9, column = 0 )

## Text entry for date
expanditure_date_string = tk.StringVar( crypto_expanditure )
expanditure_date_textbox = tk.Entry( crypto_expanditure, textvariable = expanditure_date_string )
expanditure_date_textbox.insert( 0, str( date.today().strftime('%Y-%m-%d') ) )
#expanditure_date_textbox.configure( state = 'disable' )
expanditure_date_textbox.grid( row = 10, column = 0, padx = 10 )

## Button to take action
expanditure_button = tk.Button( crypto_expanditure, text = 'Transferir', command = lambda: input_controls( 1 ) )
expanditure_button.grid( row = 11, column = 0, padx = 10, pady = 10 )

#######################################################################################################################
################################################ COMBOBOX PARA TRADING ################################################
#######################################################################################################################

trade_crypto = ttk.LabelFrame( mainWindow, text = 'Trading' )
trade_crypto.grid( row = 1, column = 0, sticky = "nswe" )

label = tk.Label( trade_crypto, text = '*Código Crypto Inicial', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_initial_string_value = tk.StringVar()
initial_crypto_trading_list = Combobox( trade_crypto, textvariable = list_initial_string_value,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
initial_crypto_trading_list['values'] = monedas_propias
initial_crypto_trading_list.grid( row = 1, column = 0, padx = 10 )

label = tk.Label( trade_crypto, text = '*Cantidad Crypto Inicial:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 2, column = 0 )

## Text entry for amount crypto
initial_amount_string_value = tk.StringVar(  trade_crypto )
initial_amount_textbox = tk.Entry( trade_crypto, textvariable = initial_amount_string_value, state = 'normal' )
initial_amount_textbox.insert( 0, '' )
initial_amount_textbox.grid( row = 3, column = 0, padx = 10 )

label = tk.Label( trade_crypto, text = '*Código Crypto Final', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 4, column = 0 )

## Combo Box for cryptos
list_final_string_value = tk.StringVar()
final_crypto_trading_list = Combobox( trade_crypto, textvariable = list_final_string_value,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
final_crypto_trading_list['values'] = monedas
final_crypto_trading_list.grid( row = 5, column = 0, padx = 10 )

label = tk.Label( trade_crypto, text = '*Cantidad Crypto Final:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 6, column = 0 )

## Text entry for amount crypto
final_amount_string_value = tk.StringVar(  trade_crypto )
final_amount_textbox = tk.Entry( trade_crypto, textvariable = final_amount_string_value, state = 'normal' )
final_amount_textbox.insert( 0, '' )
final_amount_textbox.grid( row = 7, column = 0, padx = 10 )

## Checkbox old tranfer
variable_check_old_trade = tk.IntVar( trade_crypto )
check_old_tranfer_trade = tk.Checkbutton( trade_crypto, text = 'Tranferencia Vieja', variable = variable_check_old_trade, onvalue = 1, offvalue = 0, command = lambda: change_tranfer_status( 2 ) )
#check_old_tranfer_trade.grid(row = 8, column = 0 , padx = 5, sticky = "ew")

label = tk.Label( trade_crypto, text = 'Valor Crypto Final (Al momento del Trade):', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 9, column = 0 )

## Text entry for dolar value
final_crypto_string_value = tk.StringVar( trade_crypto )
final_crypto_value_textbox = tk.Entry( trade_crypto, textvariable = final_crypto_string_value )
final_crypto_value_textbox.insert( 0, '' )
final_crypto_value_textbox.grid( row = 10, column = 0, padx = 10 )

label = tk.Label( trade_crypto, text = 'Fecha:', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 11, column = 0 )

## Text entry for date
trading_date_string = tk.StringVar( trade_crypto )
trading_date_textbox = tk.Entry( trade_crypto, textvariable = trading_date_string )
trading_date_textbox.insert( 0, str( date.today().strftime('%Y-%m-%d') ) )
trading_date_textbox.grid( row = 12, column = 0, padx = 10 )

## Button to take action
trade_button = tk.Button( trade_crypto, text = 'Ingresar Trading', command = lambda: input_controls( 2 ) )
trade_button.grid( row = 13, column = 0, padx = 10, pady = 10 )

##############################################################################################################################
################################################ COMBOBOX PARA OTRAS OPCIONES ################################################
##############################################################################################################################

other_options = ttk.LabelFrame( mainWindow, text = 'Otras Acciones' )
other_options.grid( row = 1, column = 1, sticky = "nswe" )

label = tk.Label( other_options, text = 'Crypto Code', font = ( 'Helvetica', 12 ), fg = 'black' )
label.grid( row = 0, column = 0 )

## Combo Box for cryptos
list_value_other_actions = tk.StringVar()
cripto_list_other_actions = Combobox( other_options, textvariable = list_value_other_actions,
                            state = 'readonly', height = '6',
                            justify = 'center', font = ( 'Helvetica', 12 )
                            )

## List of cryptos
cripto_list_other_actions['values'] = monedas_propias
cripto_list_other_actions.grid( row = 1, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Calcular Rentabilidad Individual', command = individual_profit_clicked )
button.grid( row = 2, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Calcular Rentabilidad Total', command = full_profit_clicked )
button.grid( row = 3, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Calcular Ganancia Individual', command = show_earns_clicked )
button.grid( row = 4, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Calcular Ganancia Total', command = show_total_earns_clicked )
button.grid( row = 5, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Mostrar Balance de Moneda', command = lambda: consultar_crypto_clicked( cripto_list_other_actions.get() ) )
button.grid( row = 6, column = 0, padx = 10, pady = 5 )

## Button to take action
button_balance_general = tk.Button( other_options, text = 'Mostrar Balance General', command = show_balance_general )
button_balance_general.grid( row = 7, column = 0, padx = 10, pady = 5 )

## Button to take action
button_balance_general = tk.Button( other_options, text = 'Generar Balance General', command = generar_balance_general )
button_balance_general.grid( row = 8, column = 0, padx = 10, pady = 5 )

## Button to take action
button = tk.Button( other_options, text = 'Generar Histórico de Transacciones', command = create_archivo_transacciones )
button.grid( row = 9, column = 0, padx = 10, pady = 5 )

## looping for GUI
mainWindow.mainloop()