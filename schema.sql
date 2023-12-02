CREATE TABLE Utenti (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(50),
        cognome VARCHAR(50),
        email VARCHAR(100)
    );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE Prodotti (
        id_prodotto INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_utente INT,
        nome_prodotto VARCHAR(100),
        prezzo DECIMAL(10, 2),
        descrizione TEXT,
        categoria_id INT,
        FOREIGN KEY (id_utente) REFERENCES Utenti(id)
    );
CREATE TABLE Ordini (
        id_ordine INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_utente INT,
        data_ordine DATE,
        stato VARCHAR(50),
        FOREIGN KEY (id_utente) REFERENCES Utenti(id)
    );
CREATE TABLE DettagliOrdine (
        id_dettaglio INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_ordine INT,
        id_prodotto INT,
        quantita INT,
        FOREIGN KEY (id_ordine) REFERENCES Ordini(id),
        FOREIGN KEY (id_prodotto) REFERENCES Prodotti(id_prodotto)
    );
