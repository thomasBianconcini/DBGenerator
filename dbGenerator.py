from flask import Flask, jsonify
import sqlite3

from faker import Faker
import pandas as pd
import os 
import subprocess

import csv

app = Flask(__name__)
fake = Faker()


def import_database():
   print("ciao")

def create_database():
    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()
    comandi_sql = [
    '''CREATE TABLE IF NOT EXISTS Utenti (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(50),
        cognome VARCHAR(50),
        email VARCHAR(100)
    );''',

    '''CREATE TABLE IF NOT EXISTS Prodotti (
        id_prodotto INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_utente INT,
        nome_prodotto VARCHAR(100),
        prezzo DECIMAL(10, 2),
        descrizione TEXT,
        categoria_id INT,
        FOREIGN KEY (id_utente) REFERENCES Utenti(id)
    );''',

    '''CREATE TABLE IF NOT EXISTS Ordini (
        id_ordine INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_utente INT,
        data_ordine DATE,
        stato VARCHAR(50),
        FOREIGN KEY (id_utente) REFERENCES Utenti(id)
    );''',

    '''CREATE TABLE IF NOT EXISTS DettagliOrdine (
        id_dettaglio INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_ordine INT,
        id_prodotto INT,
        quantita INT,
        FOREIGN KEY (id_ordine) REFERENCES Ordini(id),
        FOREIGN KEY (id_prodotto) REFERENCES Prodotti(id_prodotto)
    );'''
]
    for create_table in comandi_sql:
        c.execute(create_table)
    conn.commit()

    riempi_table = [
    '''INSERT INTO Utenti (nome, cognome, email) VALUES
        ('Mario', 'Rossi', 'mario@email.com'),
        ('Laura', 'Bianchi', 'laura@email.com'),
        ('Luca', 'Verdi', 'luca@email.com'),
        ('Chiara', 'Neri', 'chiara@email.com');''',

    '''INSERT INTO Prodotti (id_utente, nome_prodotto, prezzo, descrizione, categoria_id) VALUES
        ('1','Laptop', 1200.00, 'Laptop veloce con schermo HD', 1),
        ('2','Smartphone', 800.00, 'Smartphone con fotocamera di alta qualità', 1),
        ('3','Tastiera', 50.00, 'Tastiera meccanica retroilluminata', 2),
        ('4','Mouse', 30.00, 'Mouse ergonomico senza fili', 2);''',

    '''INSERT INTO Ordini (id_utente, data_ordine, stato) VALUES
        (1, '2023-01-15', 'Consegnato'),
        (2, '2023-02-20', 'In attesa'),
        (3, '2023-03-10', 'Spedito'),
        (4, '2023-04-05', 'Consegnato');''',

    '''INSERT INTO DettagliOrdine (id_ordine, id_prodotto, quantita) VALUES
        (1, 1, 2),
        (1, 3, 1),
        (2, 2, 1),
        (3, 4, 3),
        (4, 1, 1);'''
]
    for riempi in riempi_table:
        c.execute(riempi)
    

    conn.commit()
    conn.close()

    # Return the table as an HTML response
    
if __name__ == '__main__':
    DB_esitente = input("Hai un DB? S o N")
    if DB_esitente == "N":
       print("creating DB")
       create_database()
    else:
        import_database()
        print("importing DB")
    #comando = "docker cp test:/app/people.db /home/thomas/Desktop/progettoCyber/people.db"
    #output = subprocess.run(comando, shell=True)
    
    #app.run(debug=True, host='0.0.0.0')


    
