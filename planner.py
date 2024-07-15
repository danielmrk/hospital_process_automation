
import pandas as pd
import random as rd
from itertools import combinations
import math
from bottle import  route, run, template, request, response, HTTPResponse
import json
import sqlite3

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


@route('/planner', method = 'POST')
def planner():
    try:
        cid = request.forms.get('patientId')
        time = request.forms.get('time')
        info = request.forms.get('info')
        resources = request.forms.get('resources')
        
        #insert actual state in database
        put_feedback_to_database(resources)

        info = json.loads(info)
        print(info['diagnosis'])
        return {"test": "test"}
    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}
    
run(host='::1', port=48905)