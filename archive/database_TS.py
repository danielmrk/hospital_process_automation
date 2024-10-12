import sqlite3

# Verbindung zur SQLite-Datenbank herstellen (wenn die Datei nicht existiert, wird sie erstellt)
conn = sqlite3.connect('history_TS.db')

# Erstelle ein Cursor-Objekt
cursor = conn.cursor()

# Tabelle erstellen, falls sie noch nicht existiert
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        cid INTEGER PRIMARY KEY,
        task TEXT,
        start TEXT,
        info JSON,
        wait BOOLEAN
    )
''')

conn.commit()