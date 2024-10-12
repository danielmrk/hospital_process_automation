#! /usr/bin/python3
from bottle import  route, run, template, request, response
import sqlite3
import requests
import numpy
import json
from datetime import datetime, timedelta
import queue
import time
import random

def minutes_to_datetime(minutes):
    # Startdatum: 1. Januar 2018
    start_date = datetime(year=2018, month=1, day=1)
    
    # Minuten in ein timedelta umwandeln
    time_delta = timedelta(minutes=minutes)
    
    # Neues Datum berechnen
    result_date = start_date + time_delta
    
    return result_date

for j in range(15):
    # Generiere eine Liste mit 30 zufälligen Minuten zwischen 0 und 1439 (1440 Minuten pro Tag)
    random_minutes = random.sample(range(1440), 10)
    
    # Sortiere die Minuten aufsteigend, damit sie wie ein Tagesablauf aussehen
    random_minutes.sort()

    updated_minutes = [(minute + j * 1440) for minute in random_minutes]

    print(updated_minutes)


    for i in updated_minutes:

        print("i")
        print(minutes_to_datetime(i))
        
        randomNumber = random.random()
        patientType = "A1"

        if randomNumber < (1/9):
            patientType = "A1"
        elif randomNumber < (2/9):
            patientType = "A2"
        elif randomNumber < (3/9):
            patientType = "A3"
        elif randomNumber < (4/9):
            patientType = "A4"
        elif randomNumber < (5/9):
            patientType = "B1"
        elif randomNumber < (6/9):
            patientType = "B2"
        elif randomNumber < (7/9):
            patientType = "B3"
        elif randomNumber < (8/9):
            patientType = "B4"
        elif randomNumber < (9/9):
            patientType = "ER"

        data = {
                    "behavior": "fork_running",
                    "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main_meierkord.xml",
                    "init": "{\"patientType\":\"" + patientType + "\", \"arrivalTime\":\"" + str(i) + "\"}"
                    }
                
        response = requests.post("https://cpee.org/flow/start/url/", data = data)
        time.sleep(2)
