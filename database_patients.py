import sqlite3

# Verbindung zur SQLite-Datenbank herstellen (wenn die Datei nicht existiert, wird sie erstellt)
conn = sqlite3.connect('patients.db')

# Erstelle ein Cursor-Objekt
cursor = conn.cursor()

# Tabelle erstellen, falls sie noch nicht existiert
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patientID INTEGER PRIMARY KEY,
        admissionDate TEXT,
        patientType TEXT,
        totalTime INTEGER,
        processFinished BOOLEAN
    )
''')

conn.commit()
