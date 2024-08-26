
import pandas as pd
import random as rd
from itertools import combinations
import math
from bottle import  route, run, template, request, response, HTTPResponse
import json
import sqlite3
from datetime import datetime, timedelta


def iso_to_global_minute(iso_time):
    """
    Wandelt eine ISO 8601-Zeit in eine globale Minute bezogen auf das Jahr um.

    :param iso_time: Zeit in ISO 8601-Format (z.B. "2024-07-14T12:34:56")
    :return: Globale Minute im Jahr
    """
    # ISO 8601-Zeit in ein datetime-Objekt umwandeln
    dt = datetime.fromisoformat(iso_time)

    # Beginn des Jahres für die Berechnung
    start_of_year = datetime(year=dt.year, month=1, day=1)

    # Differenz in Minuten berechnen
    delta = dt - start_of_year
    global_minute = delta.days * 24 * 60 + delta.seconds // 60

    return global_minute

def global_minute_to_iso(year, global_minute):
    """
    Wandelt eine globale Minute bezogen auf das Jahr in eine ISO 8601-Zeit um.

    :param year: Jahr, auf das sich die globale Minute bezieht (z.B. 2024)
    :param global_minute: Globale Minute im Jahr
    :return: ISO 8601-Zeit (z.B. "2024-07-14T12:34:56")
    """
    # Beginn des Jahres
    start_of_year = datetime(year=year, month=1, day=1)

    # Zeitdifferenz berechnen
    delta = timedelta(minutes=global_minute)

    # ISO-Zeit berechnen
    iso_time = start_of_year + delta

    return iso_time.isoformat()


def create_planning_calendar():
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('planning_calender.db')
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        globalMinute INTEGER NOT NULL,
        weekday TEXT NOT NULL,
        hour INTEGER NOT NULL,
        minute INTEGER NOT NULL,
        intake INTEGER DEFAULT 0,
        surgery INTEGER DEFAULT 0,
        a_bed INTEGER DEFAULT 0,
        b_bed INTEGER DEFAULT 0,
        emergency INTEGER DEFAULT 0,
        UNIQUE(globalMinute, weekday, hour, minute)
    )
    ''')

    # Wochentage
    weekdays = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    minute_counter = 0
    # Daten einfügen
    for weeks in range(52):
        for day in weekdays:
            for hour in range(24):
                for minute in range(60):
                    if day == "Monday" or day == "Tuesday" or day == "Wednesday" or day == "Thursday" or day == "Friday":
                        if hour >= 8 and hour <= 17:
                            cursor.execute('''
                            INSERT OR IGNORE INTO resources (globalMinute, weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                            VALUES (?, ?, ?, ?, 4, 5, 30, 40 , 9)
                            ''', (minute_counter, day, hour, minute))
                        else:
                            cursor.execute('''
                            INSERT OR IGNORE INTO resources (globalMinute, weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                            VALUES (?, ?, ?, ?, 0, 1, 30, 40 , 9)
                            ''', (minute_counter, day, hour, minute))
                    else:
                        cursor.execute('''
                        INSERT OR IGNORE INTO resources (globalMinute, weekday, hour, minute, intake, surgery, a_bed, b_bed, emergency)
                        VALUES (?, ?, ?, ?, 0, 1, 30, 40 , 9)
                        ''', (minute_counter, day, hour, minute))
                    minute_counter += 1

    # Änderungen speichern und Datenbankverbindung schließen
    conn.commit()
    conn.close()



def put_planned_to_database(cid, currentTime, diagnosis, plannedTime):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('planned_database.db')  # Ersetze 'your_database.db' mit deinem Datenbanknamen
    cursor = conn.cursor()

    # Tabelle erstellen, falls sie noch nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            cid INTEGER PRIMARY KEY,
            currenTime TEXT,
            diagnosis TEXT,
            plannedTime TEXT
        )
    ''')

    # Datenpunkt einfügen
    cursor.execute('''
        INSERT INTO patients (cid, currentTime, diagnosis, plannedTime)
        VALUES (?, ?, ?, ?)
    ''', (cid, currentTime, diagnosis, plannedTime))

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

def put_feedback_to_database(resources):
    conn = sqlite3.connect('status_database.db')  # Ersetze 'your_database.db' mit deinem Datenbanknamen
    cursor = conn.cursor()

    # Tabelle erstellen, falls sie noch nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            cid INTEGER PRIMARY KEY,
            task TEXT,
            start TEXT,
            info TEXT,
            wait BOOLEAN,
        )
    ''')
    for case in resources:
        # Datenpunkt einfügen
        case = json.loads(case)
        cid = case['cid']
        task = case['task']
        start = case['start']
        info = case['info']
        wait = case['wait']
        cursor.execute('''
            INSERT INTO patients (cid, task, start, info, wait)
            VALUES (?, ?, ?, ?, ?)
        ''', (cid, task, start, info, wait))

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

# Initiale Lösung generieren (einfache Zuordnung von Patienten zu Zeitslots)
def generate_initial_solution(time, patientType):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()

    #calculate intake duration
    intakeDuration = 60

    #calculate mean of duration of surgery
    if patientType == "A1" or patientType == "B1" or patientType == "B2":
        surgeryDuration = 0
    elif patientType == "A2":
        surgeryDuration = 60
    elif patientType == "A3":
        surgeryDuration = 120
    elif patientType == "A4" or patientType == "B3" or patientType == "B4":
        surgeryDuration = 240
    
    #calculate mean of duration of nursing
    if patientType == "A1":
        nursingDuration = 240
    elif patientType == "A2" or patientType == "B1":
        nursingDuration = 480
    else:
        nursingDuration = 960

    
    
def find_next_available_timeslot(start_time, intake_duration, surgery_duration, nursing_duration):
    """
    Prüft, ob Ressourcen für die angegebene Dauer in der Reihenfolge Intake, Surgery, Nursing frei sind.
    """
    conn = sqlite3.connect('planning_calender.db')
    cursor = conn.cursor()

    start_minute = iso_to_global_minute(start_time)
    total_duration = intake_duration + surgery_duration + nursing_duration

    def check_sequence(start_minute):
        cursor.execute('''
        SELECT globalMinute
        FROM resources
        WHERE globalMinute >= ? AND globalMinute < ? AND intake > 0
        ORDER BY globalMinute
        ''', (start_minute, start_minute + intake_duration))
        intake_slots = cursor.fetchall()

        if len(intake_slots) == intake_duration:
            start_minute = intake_slots[-1][0] + 1
            cursor.execute('''
            SELECT globalMinute
            FROM resources
            WHERE globalMinute >= ? AND globalMinute < ? AND surgery > 0
            ORDER BY globalMinute
            ''', (start_minute, start_minute + surgery_duration))
            surgery_slots = cursor.fetchall()

            if len(surgery_slots) == surgery_duration:
                start_minute = surgery_slots[-1][0] + 1
                cursor.execute('''
                SELECT globalMinute
                FROM resources
                WHERE globalMinute >= ? AND globalMinute < ? AND a_bed > 0 AND b_bed > 0
                ORDER BY globalMinute
                ''', (start_minute, start_minute + nursing_duration))
                nursing_slots = cursor.fetchall()

                if len(nursing_slots) == nursing_duration:
                    return intake_slots, surgery_slots, nursing_slots
        return None

    cursor.execute('SELECT globalMinute FROM resources WHERE globalMinute >= ? ORDER BY globalMinute', (start_minute,))
    all_minutes = cursor.fetchall()

    for (minute,) in all_minutes:
        result = check_sequence(minute)
        if result:
            intake_slots, surgery_slots, nursing_slots = result
            iso_start = global_minute_to_iso(datetime.now().year, intake_slots[0][0])
            print(f"Nächster verfügbarer Zeitslot:")
            print(f"Startzeit: {iso_start}")
            return iso_start

    print("Kein verfügbarer Zeitslot gefunden.")
    conn.close()


# Bewertungsfunktion (z.B. Minimierung von Wartezeiten)
def evaluate_solution(solution):
    # Dummy-Bewertungsfunktion, implementiere hier die echte Logik
    return sum(slot for slot in solution.values())


@route('/planner', method = 'POST')
def planner():
    try:
        cid = request.forms.get('patientId')
        time = request.forms.get('time')
        info = request.forms.get('info')
        resources = request.forms.get('resources')
        
        #insert actual state in database
        #put_feedback_to_database(resources)

        info = json.loads(info)
        print(info['diagnosis'])
        return {"test": "test"}
    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}

create_planning_calendar()  
run(host='::1', port=48905)