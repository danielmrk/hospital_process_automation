#! /usr/bin/python3
import sqlite3
import numpy
import json
from datetime import datetime
import queue
import time
import random
import random
from datetime import datetime, timedelta
from planner import Planner

# Beispielhafte Patientenarten
patient_types = ['A1', 'B1', 'A2', 'B4']

# Patientendaten generieren
def generate_patient(patient_id):
    data = dict()
    
    # Patient ID
    data['cid'] = patient_id
    
    # Zufällige Ankunftszeit im heutigen Tag
    today = datetime(2018, 1, 1)
    random_minutes = random.randint(0, 24 * 60 - 1)  # Zufällige Minute des Tages
    arrival_time = today + timedelta(minutes=random_minutes)
    
    data['time'] = arrival_time # Ankunftszeit als UNIX-Timestamp
    
    # Zufälliger Patiententyp
    info = dict()
    info['diagnosis'] = random.choice(patient_types)

    data['info'] = info
    
    # Platzhalter für Ressourcen
    data['resources'] = "Placeholder"
    
    return data

# Liste von 30 zufälligen Patienten erstellen
patients = [generate_patient(i) for i in range(1, 150)]

# Ergebnis anzeigen
for patient in patients:
    print(patient)

planner = Planner("./temp/event_log1.csv", ["diagnosis"])
planner.plan(patients)

