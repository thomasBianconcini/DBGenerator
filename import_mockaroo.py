import re
import pprint

def import_database():

    #schemaUrl= input("Inserisci path file (schema.sql)\n")
    schemaUrl="schema.sql"

    list_commands=[]

    with open(schemaUrl,"r") as file:
        sqlite_file=file.read()
        commands= sqlite_file.split(";")
        for command in commands:
            if command!="" and command!="\n":
                command=command + ";"
                if "sqlite_sequence" not in command:
                    #print("COMMAND:",command)
                    list_commands.append(command)

    
    table_names=[]
    clean_att=[]

    for command in list_commands:
        pattern_a = r"([a-z_]+) \w+\(?\d*\)?"
        pattern_t=r'\bCREATE TABLE (\w+)'
        column_names = re.findall(pattern_a, command)
        clean_att.append(column_names)
        #print("ATTRIBUTI estratto con re: ",column_names)
        column_names = re.findall(pattern_t, command)
        table_names.append(column_names[0])
        #print("TABLENAME estratto con re: ",column_names)

    print(table_names)
    print(clean_att)



if __name__ == '__main__':
    print("eseguo dell'import database()")
    import_database() #CASO IMPORT DATABASE
    # clean att= [[a1,a2,a3], [b1,b2,b3],[c1,c2,c3]]

"""
---COMMAND:  CREATE TABLE Utenti (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(50),
        cognome VARCHAR(50),
        email VARCHAR(100)
    );

---COMMAND:  
CREATE TABLE Prodotti (
        id_prodotto INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_utente INT,
        nome_prodotto VARCHAR(100),
        prezzo DECIMAL(10, 2),
        descrizione TEXT,
        categoria_id INT,
        FOREIGN KEY (id_utente) REFERENCES Utenti(id)
    );
---COMMAND:  
CREATE TABLE DettagliOrdine (
        id_dettaglio INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_ordine INT,
        id_prodotto INT,
        quantita INT,
        FOREIGN KEY (id_ordine) REFERENCES Ordini(id),
        FOREIGN KEY (id_prodotto) REFERENCES Prodotti(id_prodotto)
    );

---COMMAND:  
;

"""