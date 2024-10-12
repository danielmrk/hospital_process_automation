#! /usr/bin/python3
from bottle import  route, run, template, request, response, HTTPResponse
import sqlite3
import requests
import numpy
import json
from datetime import datetime
import queue
import time as tm
import random
import threading
from datetime import datetime, timedelta
import os
import subprocess
from planner import Planner
import math
import logging


datei_zum_loeschen = "hospital.log"
if os.path.exists(datei_zum_loeschen):
    os.remove(datei_zum_loeschen)
    print(f"{datei_zum_loeschen} wurde gelöscht.")
else:
    print(f"{datei_zum_loeschen} existiert nicht.")

# Konfiguriere das Logging
logging.basicConfig(
    filename='hospital.log',          # Log-Datei, in die Ereignisse geschrieben werden
    filemode='a',                # 'a' für Anhängen, 'w' würde überschreiben
    level=logging.INFO,          # Setzt das Mindest-Log-Level (z. B. INFO, DEBUG, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log-Format
)

taskQueue = queue.PriorityQueue()
taskQueueReplanning = queue.PriorityQueue()

#Amount of surgery in the queue
surgeryNursingQueue = queue.Queue()

replanning = False


#Array for initial state in minutes
state_array = [[] for _ in range(525600)]
day_array_a_nursing = [30] * 525600
day_array_b_nursing = [40] * 525600
day_array_emergency = [9] * 525600

# Counter and time variable for time management
simulationTime = 0
dayCounter = 0
planningFinal = False

# Jahr mit Startdatum festlegen
jahr_start = datetime(2018, 1, 1)
jahr_minuten = 365 * 24 * 60  # Anzahl Minuten im Jahr (ohne Schaltjahr)

day_array_intake = [None] * 525600
day_array_surgery = [None] * 525600

plannable_elements = []

# Array füllen: 5 zwischen 08:00 und 17:00 Uhr, sonst 7
for i in range(jahr_minuten):
    aktuelle_zeit = jahr_start + timedelta(minutes=i)
    wochentag = aktuelle_zeit.weekday()  # 0 = Montag, ..., 6 = Sonntag
    if wochentag < 5:
        if 8 <= aktuelle_zeit.hour < 17:
            day_array_intake[i] = 4
            day_array_surgery[i] = 5
        else:
            day_array_surgery[i] = 1
            day_array_intake[i] = 0
    else:
        day_array_surgery[i] = 1
        day_array_intake[i] = 0

print("Erfolgreich erstellt")

# Class for prioritising tasks by time
class PrioritizedItem:
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __repr__(self):
        return f'PrioritizedItem(priority={self.priority}, data={self.data})'

# inserts patients into the database    
def insert_patient(admission_date, patient_type):
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO patients (admissionDate, patientType, totalTime)
        VALUES (?, ?, ?)
    ''', (admission_date, patient_type, 0))
    conn.commit()
    conn.close()
    return cursor.lastrowid


#updates the resource amount in the arrays for keeping track on resource management
def update_resource_amount(dayarray, update, startTime, endTime):
    if dayarray == 1:
        day_array_intake[startTime:endTime] = [update] * int(endTime - startTime)
    elif dayarray == 2:
        day_array_surgery[startTime:endTime] = [update] * int(endTime - startTime)
    elif dayarray == 3:
        day_array_a_nursing[startTime:endTime] = [update] * int(endTime - startTime)
    elif dayarray == 4:
        day_array_b_nursing[startTime:endTime] = [update] * int(endTime - startTime)
    elif dayarray == 5:
        day_array_emergency[startTime:endTime] = [update] * int(endTime - startTime)
    else:
        raise Exception("Updated failed")

    return dayarray

# returns the resource amount
def get_resource_amount(day_array, time):
    return day_array[time]

def set_final_planning(bool):
    global planningFinal
    planningFinal = bool

timerGlobal = threading.Timer(20, set_final_planning, args=True)
    
# updates the total time of the patient
def set_patient_time(patient_id, new_total_time):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Update-Abfrage ausführen
    cursor.execute('''
        UPDATE patients
        SET totalTime = ?
        WHERE patientID = ?
    ''', (new_total_time, patient_id))

    # Änderungen speichern
    conn.commit()

    # Überprüfen, ob die Aktualisierung erfolgreich war
    if cursor.rowcount == 0:
        print(f"Patient mit patientID {patient_id} wurde nicht gefunden.")
    else:
        print(f"Die totalTime des Patienten mit patientID {patient_id} wurde auf {new_total_time} Stunden aktualisiert.")

    # Verbindung schließen
    conn.close()

# sets patients first arrivalTime
def set_patient_arrivalTime(patient_id, new_arrival_time):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Update-Abfrage ausführen
    cursor.execute('''
        UPDATE patients
        SET arrivalTime = ?
        WHERE patientID = ?
    ''', (new_arrival_time, patient_id))

    # Änderungen speichern
    conn.commit()

    # Überprüfen, ob die Aktualisierung erfolgreich war
    if cursor.rowcount == 0:
        print(f"Patient mit patientID {patient_id} wurde nicht gefunden.")
    else:
        print(f"Die totalTime des Patienten mit patientID {patient_id} wurde auf {new_arrival_time} Stunden aktualisiert.")

    # Verbindung schließen
    conn.close()

# gets the patient arrivaltime
def get_arrival_time(patientId):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Abfrage ausführen
    cursor.execute('''
        SELECT arrivalTime FROM patients
        WHERE patientID = ?
    ''', (patientId,))

    # Ergebnis abrufen (es sollte nur ein Ergebnis geben)
    result = cursor.fetchone()

    # Verbindung schließen
    conn.close()

    # Wenn ein Ergebnis vorhanden ist, gib die totalTime zurück, sonst gib None zurück
    if result:
        return result[0]  # Das erste Element des Ergebnis-Tupels ist die totalTime
    else:
        return None

def time_to_global_minutes(t):
        """
        Wandelt ein datetime.time-Objekt in globale Minuten seit Mitternacht um.
        
        :param t: Ein datetime.time-Objekt
        :return: Anzahl der Minuten seit Mitternacht
        """
        return t.hour * 60 + t.minute + t.second / 60

def minutes_to_datetime(minutes):
    # Startdatum: 1. Januar 2018
    start_date = datetime(year=2018, month=1, day=1)
    
    # Minuten in ein timedelta umwandeln
    time_delta = timedelta(minutes=minutes)
    
    # Neues Datum berechnen
    result_date = start_date + time_delta
    
    return result_date

def set_process_status(patient_id, status):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Update-Abfrage ausführen
    cursor.execute('''
        UPDATE patients
        SET processFinished = ?
        WHERE patientID = ?
    ''', (status, patient_id))

    # Änderungen speichern
    conn.commit()

    # Überprüfen, ob die Aktualisierung erfolgreich war
    if cursor.rowcount == 0:
        print(f"Patient mit patientID {patient_id} wurde nicht gefunden.")
    else:
        print(f"Der Finish Status des Patienten mit patientID {patient_id} wurde auf {status} geändert.")

    # Verbindung schließen
    conn.close()

def calculate_operation_time(diagnosis, operation):
    if operation == "surgery":
        if diagnosis == "A2":
            return numpy.random.normal(60, 15)
        if diagnosis == "A3":
            return numpy.random.normal(120, 30)
        if diagnosis == "A4":
            return numpy.random.normal(240, 30)
        if diagnosis == "B3":
            return numpy.random.normal(240, 30)
        if diagnosis == "B4":
            return numpy.random.normal(240, 60)
        else:
            print("Incorrect PatientType")
            return None
    if operation == "nursing":
        if diagnosis == "A1":
            return numpy.random.normal(240, 30)
        if diagnosis == "A2":
            return numpy.random.normal(480, 120)
        if diagnosis == "A3":
            return numpy.random.normal(960, 120)
        if diagnosis == "A4":
            return numpy.random.normal(960, 120)
        if diagnosis == "B1":
            return numpy.random.normal(480, 120)
        if diagnosis == "B2":
            return numpy.random.normal(960, 120)
        if diagnosis == "B3":
            return numpy.random.normal(960, 240)
        if diagnosis == "B4":
            return numpy.random.normal(960, 240)
        else:
            print("Incorrect PatientType")
            return None
    else:
        print("Incorrect Operation")
        return None
    
def complication_generator(patientType):
    if patientType == "A1":
        probability = 0.01
    elif patientType == "A2":
        probability = 0.01
    elif patientType == "A3":
        probability = 0.02
    elif patientType == "A4":
        probability = 0.02
    elif patientType == "B1":
        probability = 0.001
    elif patientType == "B2":
        probability = 0.01
    elif patientType == "B3":
        probability = 0.02
    elif patientType == "B4":
        probability = 0.02
    else:
        probability = 0

    random_number = random.random()

    if random_number < probability:
        complication = True
    else:
        complication = False
    return complication

def ER_diagnosis_generator():
    random_number = random.random()
    print(random_number)
    if random_number > 0.75:
        diagnosis = "A1"
    elif random_number > 0.625:
        diagnosis = "A2"
    elif random_number > 0.5625:
        diagnosis = "A3"
    elif random_number > 0.5:
        diagnosis = "A4"
    elif random_number > 0.25:
        diagnosis = "B1"
    elif random_number > 0.125:
        diagnosis = "B2"
    elif random_number > 0.0625:
        diagnosis = "B3"
    else:
        diagnosis = "B4"
    return diagnosis



@route('/task', method = 'POST')
def task_queue():
    try:
        #load patient data
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        arrivalTime = request.forms.get('arrivalTime')
        patientTime = request.forms.get('patientTime')
        appointment = request.forms.get('appointment')
        taskRole = request.forms.get('taskRole')
        callbackURL = request.headers['CPEE-CALLBACK']

        data = {"patientId": patientId,
                "patientType": patientType,
                "arrivalTime": arrivalTime,
                "patientTime": patientTime,
                "appointment": appointment,
                "taskRole": taskRole,
                "callbackURL": callbackURL}

        #add task to the queue to process it by the worker and prioritize it by patient time
        data = json.dumps(data)
        if taskRole == "patientAdmission":
            patientTime = arrivalTime
            taskQueue.put(PrioritizedItem(int(patientTime), data))
        else:
            taskQueue.put(PrioritizedItem(int(patientTime), data))

        #Queue to check how many patients are in surgery or nursing queue
        if taskRole == "surgery" or taskRole == "nursing":
            surgeryNursingQueue.put("Patient")

        # Return the HHTP Response to respond later
        return HTTPResponse(
            json.dumps({'Ack.:': 'Response later'}),
            status=202,
            headers={'content-type': 'application/json', 'CPEE-CALLBACK': 'true'})
    
    

    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}
    

def worker():
    while True:
        try:
            global day_array_intake
            global day_array_a_nursing
            global day_array_b_nursing
            global day_array_emergency
            global day_array_surgery

            tm.sleep(0.5)
            task = taskQueue.get()
            task = json.loads(task.data)
            patientId = task['patientId']
            patientType = task['patientType']
            arrivalTime = task['arrivalTime']
            patientTime = task['patientTime']
            appointment = task['appointment']
            taskRole = task['taskRole']
            callbackURL= task['callbackURL']
            with open('arrivaltime.txt', 'a') as file:
                file.write(f"{arrivalTime}\n")
            with open('patientTime.txt', 'a') as file:
                file.write(f"{patientTime}\n")
            if taskRole != "patientAdmission":
                logging.info("patientId: " + str(patientId) + ", patientType: " + str(patientType) + ", TaskRole: " + taskRole +  ", Patienttime: " + str(minutes_to_datetime(int(patientTime))))
        

            if taskRole == "patientAdmission":
                #print("test")
                #set patienttime to arrivaltime for this run
                patientTime = int(arrivalTime)
                global state_array

                #convert patienttime in correct format
                start_date = datetime(2018, 1, 1)
    
                # Füge die Minuten hinzu
                result_time = start_date + timedelta(minutes = patientTime)
                
                # Rückgabe im ISO 8601-Format
                timeISO = result_time.isoformat()

                #Assign PatientId if there is no and put patient into patient database
                if not patientId:
                    patientId = insert_patient(arrivalTime, patientType)
                    set_patient_arrivalTime(patientId, arrivalTime)
                    global simulationTime
                    simulationTime = int(arrivalTime)
                else:
                    pass
                logging.info("patientId: " + str(patientId) + ", patientType: " + str(patientType) + ", TaskRole: " + taskRole +  ", Patienttime: " + str(minutes_to_datetime(int(patientTime))))
                #check if resources are available if patient has appointment
                # print("Test:")
                # print(get_resource_amount("intake", patientTime))
                # print(surgeryNursingQueue.qsize())
                # print(patientTime)
                if appointment:           
                    if get_resource_amount(day_array_intake, int(patientTime)) > 0 and surgeryNursingQueue.qsize() < 3:
                        intake = True
                    else:
                        intake = False
                elif patientType == "ER":
                    intake = True
                else:
                    intake = False

                                # Prepare the callback response as JSON
                callback_response = {
                    'patientType': patientType,
                    'patientId': patientId, 
                    'patientTime': patientTime,
                    'intake': intake,
                    'time' : timeISO
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }

                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")

            elif taskRole == "intake":
                #calculate intake duration
                intake_duration = round(numpy.random.normal(60, 7.5))

                #book resources
                amount = get_resource_amount(day_array_intake, int(patientTime))
                if amount > 0:
                    update_resource_amount(1, (amount - 1), int(patientTime), int(patientTime) + int(intake_duration))
                    for i in range(int(patientTime), int(patientTime) + intake_duration):
                        state_array[i].append({'cid': patientId, 'task': 'intake', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                else:
                    while get_resource_amount(day_array_intake, int(patientTime)) < 1:
                        patientTime = int(patientTime) + 1
                        state_array[int(patientTime)].append({'cid': patientId, 'task': 'intake', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': True})
                        print("Waiting")
                    amount = get_resource_amount(day_array_intake, int(patientTime))
                    update_resource_amount(1, (amount - 1), int(patientTime), int(patientTime) + intake_duration )
                    for i in range(int(patientTime), int(patientTime) + int(intake_duration)):
                        state_array[i].append({'cid': patientId, 'task': 'intake', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})

                #decide if patient needs surgery
                if "a" in patientType.lower():
                    if "2" in patientType or "3" in patientType or "4" in patientType:
                        surgery = True
                    else:
                        surgery = False
                elif "b" in patientType.lower():
                    if "3" in patientType or "4" in patientType:
                        surgery = True
                    else:
                        surgery = False
                else:
                    surgery = False

                #set patientTime to new Time
                patientTime = int(patientTime) + intake_duration

                # Prepare the callback response as JSON
                callback_response = {
                    'phantomPain': False,
                    'patientTime': patientTime,
                    'surgery': surgery
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }

                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")


            elif taskRole == "surgery":
                
                #deque surgery nursing queue
                surgeryNursingQueue.get()
                surgeryNursingQueue.task_done()
                
                #calculate surgery duration
                surgeryDuration = round(calculate_operation_time(patientType[-2:], "surgery"))

                #book resources
                amount = get_resource_amount(day_array_surgery, int(patientTime))
                if amount > 0:
                    update_resource_amount(2, (amount - 1), int(patientTime), int(patientTime) + int(surgeryDuration) )
                    for i in range(int(patientTime), int(patientTime) + int(surgeryDuration)):
                        state_array[i].append({'cid': patientId, 'task': 'surgery', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                else:
                    while get_resource_amount(day_array_surgery, int(patientTime)) < 1:
                        patientTime = int(patientTime) + 1
                        print("Waiting")
                        state_array[int(patientTime)].append({'cid': patientId, 'task': 'surgery', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': True})
                    amount = get_resource_amount(day_array_surgery,int(patientTime))
                    update_resource_amount(2, (amount - 1), int(patientTime), int(patientTime) + int(surgeryDuration) )
                    for i in range(int(patientTime), int(patientTime) + int(surgeryDuration)):
                        state_array[i].append({'cid': patientId, 'task': 'surgery', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})


                #new patientTIme
                patientTime = int(patientTime) + surgeryDuration

                # Prepare the callback response as JSON
                callback_response = {
                    'patientTime': patientTime
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }
                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")

            elif taskRole == "nursing":

                #deque surgery nursing queue
                surgeryNursingQueue.get()
                surgeryNursingQueue.task_done()

                #calculate nursing duration
                nursingDuration = round(calculate_operation_time(patientType[-2:], "nursing"))
                
                #decide which resource
                if "a" in patientType.lower():
                    #book resources
                    amount = get_resource_amount(day_array_a_nursing, int(patientTime))
                    if amount > 0:
                        update_resource_amount(3, (amount - 1), int(patientTime), int(patientTime) + int(nursingDuration))
                        for i in range(int(patientTime), int(patientTime) + int(nursingDuration)):
                            state_array[i].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                    else:
                        while get_resource_amount(day_array_a_nursing, int(patientTime)) < 1:
                            patientTime = int(patientTime) + 1
                            print("Waiting")
                            state_array[int(patientTime)].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': True})
                        amount = get_resource_amount(day_array_a_nursing, int(patientTime))
                        update_resource_amount(3, (amount - 1), int(patientTime), int(patientTime) + int(nursingDuration))
                        for i in range(int(patientTime), int(patientTime) + int(nursingDuration)):
                            state_array[i].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                elif "b" in patientType.lower():
                        #book resources
                    amount = get_resource_amount(day_array_b_nursing, int(patientTime))
                    if amount > 0:
                        update_resource_amount(4, (amount - 1), int(patientTime), int(patientTime) + int(nursingDuration))
                        for i in range(int(patientTime), int(patientTime) + int(nursingDuration)):
                            state_array[i].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                    else:
                        while get_resource_amount(day_array_b_nursing, int(patientTime)) < 1:
                            patientTime = int(patientTime) + 1
                            logging.info("patientId: " + str(patientId) + ", patientType: " + str(patientType) + ", TaskRole: " + taskRole +  ", Patienttime: " + str(patientTime) + ", Waiting: True")
                            state_array[int(patientTime)].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': True})
                        amount = get_resource_amount(day_array_b_nursing, int(patientTime))
                        update_resource_amount(4, (amount - 1), int(patientTime), int(patientTime) + int(nursingDuration))
                        for i in range(int(patientTime), int(patientTime) + int(nursingDuration)):
                            state_array[i].append({'cid': patientId, 'task': 'nursing', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                else:
                    raise Exception("Patienttype not identified")


                #generate complications
                complication = complication_generator(patientType)
                #new patientTIme
                patientTime = int(patientTime) + nursingDuration
                # Prepare the callback response as JSON
                callback_response = {
                    'patientTime': patientTime,
                    'complication': complication
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }

                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")
                
            elif taskRole == "ERTreatment":

                ERDuration = round(numpy.random.normal(120,30))

                #book resources
                amount = get_resource_amount(day_array_emergency, int(patientTime))
                if amount > 0:
                    update_resource_amount(5, (amount - 1), int(patientTime), int(patientTime) + int(ERDuration))
                    for i in range(int(patientTime), int(patientTime) + ERDuration):
                        state_array[i].append({'cid': patientId, 'task': 'ERTreatment', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})
                else:
                    while get_resource_amount(day_array_emergency, int(patientTime)) < 1:
                        patientTime = int(patientTime) + 1
                        state_array[int(patientTime)].append({'cid': patientId, 'task': 'ERTreatment', 'start': patientTime/60 , 'info': {'diagnosis': patientType}, 'wait': True})
                    amount = get_resource_amount(day_array_emergency, int(patientTime))
                    update_resource_amount(5, (amount - 1), int(patientTime), int(patientTime) + int(ERDuration))
                    for i in range(int(patientTime), int(patientTime) + ERDuration):
                        state_array[i].append({'cid': patientId, 'task': 'ERTreatment', 'start': int(patientTime)/60 , 'info': {'diagnosis': patientType}, 'wait': False})

                diagnosis = ER_diagnosis_generator()
                patientType = str(patientType+"-"+diagnosis)

                #decide if patient needs surgery
                if "a" in patientType.lower():
                    if "2" in patientType or "3" in patientType or "4" in patientType:
                        surgery = True
                    else:
                        surgery = False
                elif "b" in patientType.lower():
                    if "3" in patientType or "4" in patientType:
                        surgery = True
                    else:
                        surgery = False
                else:
                    surgery = False

                #decide if patient has phantom pain
                random_number = random.random()
                if random_number > 0.5:
                    phantomPain = True
                else:
                    phantomPain = False

                patientTime = int(patientTime) + ERDuration

                # Prepare the callback response as JSON
                callback_response = {
                    'patientTime': patientTime,
                    'surgery': surgery,
                    'phantomPain': phantomPain,
                    'patientType': patientType
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }

                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")
            elif taskRole == "releasing":
                # set patienttime to final total time in the database and set the process status to finished
                set_patient_time(patientId, (int(patientTime) - int(arrivalTime)))
                set_process_status(patientId , True)
                callback_response = {
                    'patientType': patientType,
                    'patientId': patientId,
                }

                # Prepare the headers
                headers = {
                    'content-type': 'application/json',
                    'CPEE-CALLBACK': 'true'
                }

                # Send the callback response as a JSON payload
                requests.put(callbackURL, headers=headers, json=callback_response)
                print(f"PUT request sent to callback_url: {callbackURL}")
            else:
                print("Ungültige Taskrole")
            logging.info("patientId: " + str(patientId) + ", patientType: " + str(patientType) + ", TaskRole: " + taskRole + " beendet" +  ", Patienttime: " + str(minutes_to_datetime(int(patientTime))))    
            taskQueue.task_done()
        except Exception as e:
            response.status = 500
            print(e)
            return {"error": str(e)}
        
def replanning_worker():
    while True:
        try:
            global dayCounter
            global simulationTime
            global replanning
            tm.sleep(1)
            task = taskQueueReplanning.get()
            task = json.loads(task.data)
            cid = task['cid']
            info = task['info']
            resources = task['resources']
            time = task['time']
            if math.floor((simulationTime/60/24)) > dayCounter:
                    replanning = True
                    dayCounter = dayCounter + 1
            if int(time) > (dayCounter + 1) * 24 * 60:
                print("Planning zu früh")
                data = {"info": info,
                        "cid": cid,
                        "time": time,
                        "resources": resources}

                #add task to the queue to process it by the worker and prioritize it by patient time
                data = json.dumps(data)
                taskQueueReplanning.put(PrioritizedItem(int(2), data))

            else:

                print("dayCounter")
                print(math.floor((simulationTime)))
                print(dayCounter)

                try:
                    info = json.loads(info)           
                except json.JSONDecodeError:
                    print("Error: 'info' ist kein gültiger JSON-String")

                data = dict()
                data['cid'] = cid
                data['time'] = int(time)
                data['info'] = info
                data['resources'] = resources
                logging.info("patientId: " + str(cid) + ", Replanning angefangen, Data: " + str(data))        
                global plannable_elements
                global state_array
                plannable_elements.append(data)

                global planningFinal
                if replanning or planningFinal:
                    planned_elements = planner.plan(plannable_elements)
                    logging.info("DayCount: " + str(dayCounter) +", Planned Elements: " + str(planned_elements))
                    plannable_elements = []
                    with open('array.txt', 'w') as file:
                        for item in state_array:
                            file.write(f"{item}\n")  # Schreibe jedes Element in einer neuen Zeile

                        print("Array wurde in 'array.txt' gespeichert.")

                    for case in planned_elements:
                        print("Diff Time: ")
                        print(((float(case[2]) * 60 + (dayCounter + 2) * 60 * 24) - get_arrival_time(int(case[0]))))
                        if ((float(case[2]) * 60 + (dayCounter + 2) * 60 * 24) - get_arrival_time(int(case[0]))) > 10080:
                            logging.info("patientId: " + str(case[0]) + ", TaskRole: Left the Hospital after 7 days")
                        else:
                            data = {
                                'behavior': 'fork_running',
                                'url': 'https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main_meierkord.xml',
                                'init': json.dumps({
                                    'info': json.dumps({
                                        'diagnosis': str(case[1]['diagnosis'])
                                    }),
                                    'patientType': str(case[1]['diagnosis']),
                                    'patientId': str(case[0]),
                                    'arrivalTime': str(int(float(case[2]) * 60 + (dayCounter + 2) * 60 * 24)),
                                    'appointment': 'True'
                                })
                            }
                            with open('replan.txt', 'a') as file:
                                    file.write(f"{data}\n")  # Schreibe jedes Element in einer neuen Zeile
                            logging.info("patientId: " + str(case[0]) + ", patientType: " + str(case[1]['diagnosis']) + ", TaskRole: Replan" +  ", ReplanTime " + str(minutes_to_datetime(int(float(case[2]) * 60 + dayCounter * 60 * 24))))
                            response = requests.post("https://cpee.org/flow/start/url/", data = data)
                            planningFinal = False
                replanning = False
                taskQueueReplanning.task_done()


        except Exception as e:
            response.status = 500
            return {"error": str(e)}

#start Thread for the worker
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=replanning_worker, daemon=True).start()

#threading.Thread(target=timeSimulator).start()
planner = Planner("./temp/event_log1.csv", ["diagnosis"])

@route('/replanPatient', method = 'POST')
def replan_patient():
    try:
        #read out patient information
        info = request.forms.get('info')
        cid = request.forms.get('cid')
        time = request.forms.get('time')
        resources = request.forms.get('resources')
        # timerGlobal.cancel()
        # timerGlobal.start()


        data = {"info": info,
                "cid": cid,
                "time": time,
                "resources": resources}

        #add task to the queue to process it by the worker and prioritize it by patient time
        data = json.dumps(data)
        taskQueueReplanning.put(PrioritizedItem(int(1), data))

        logging.info("patientId: " + str(cid) +  ", TaskRole: Replanning detected" +  ", Data " + str(data))

        return {"patientType": info, "patientId": cid}

    except Exception as e:
        response.status = 500
        return {"error": str(e)}
    
@route('/get_state', method = 'POST')
def get_system_state():
    try:
        arrivalTime = request.forms.get('arrivalTime')
        system_state = state_array[int(arrivalTime)]
        return {"resources": system_state}

    except Exception as e:
        response.status = 500
        return {"error": str(e)}
    

run(host='::1', port=48904)
