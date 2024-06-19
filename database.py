import sqlite3

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('resources_calender.db')
cursor = conn.cursor()

# Tabelle erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekday TEXT NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    intake INTEGER DEFAULT 0,
    surgery INTEGER DEFAULT 0,
    a_bed INTEGER DEFAULT 0,
    b_bed INTEGER DEFAULT 0,
    emergency INTEGER DEFAULT 0,
    UNIQUE(weekday, hour, minute)
)
''')

# Wochentage
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Daten einfügen
for day in weekdays:
    for hour in range(24):
        for minute in range(60):
            if day == "Monday" or day == "Tued" or day == "Monday" or day == "Monday" or day == "Monday":
                if hour >= 8 and hour <= 17:
                    cursor.execute('''
                    INSERT OR IGNORE INTO resources (weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                    VALUES (?, ?, ?, 4, 5, 30, 40 , 9)
                    ''', (day, hour, minute))
                else:
                    cursor.execute('''
                    INSERT OR IGNORE INTO resources (weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                    VALUES (?, ?, ?, 0, 1, 30, 40 , 9)
                    ''', (day, hour, minute))
            else:
                cursor.execute('''
                INSERT OR IGNORE INTO resources (weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                VALUES (?, ?, ?, 0, 1, 30, 40 , 9)
                ''', (day, hour, minute))

# Änderungen speichern und Datenbankverbindung schließen
conn.commit()
conn.close()

