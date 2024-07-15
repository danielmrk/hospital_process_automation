
import pandas as pd
import random as rd
from itertools import combinations
import math
from bottle import  route, run, template, request, response, HTTPResponse
import json
import sqlite3
from datetime import datetime, timedelta

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