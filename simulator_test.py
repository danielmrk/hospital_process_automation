#! /usr/bin/python3
from bottle import  route, run, template, request, response, HTTPResponse
import sqlite3
import requests
import numpy
import json
from datetime import datetime
import queue
import time
import random
import threading


taskQueue = queue.PriorityQueue()

#Amount of surgery in the queue
surgeryQueue = 0

#Amount of nursing in the queue
nursingQueue = 0


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

def update_resource_amount(resourceName, amount, time):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE resources
        SET ? = ?
        WHERE globalMinute = ?
    ''', (resourceName, amount, time))
    conn.commit()
    conn.close()

def get_resource_amount(resource_name, time):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()

    # Abfrage ausführen
    query = f'SELECT {resource_name} FROM resources WHERE globalMinute = ?'
    cursor.execute(query, (time,))

    # Ergebnis abrufen (es sollte nur ein Ergebnis geben)
    result = cursor.fetchone()

    # Verbindung schließen
    conn.close()
    # Wenn ein Ergebnis vorhanden ist, gib die totalTime zurück, sonst gib None zurück
    if result:
        return result[0]  # Das erste Element des Ergebnis-Tupels ist die totalTime
    else:
        return None

def get_patient_time(patientId):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Abfrage ausführen
    cursor.execute('''
        SELECT totalTime FROM patients
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
            return numpy.random.normal(1, 0.25)
        if diagnosis == "A3":
            return numpy.random.normal(2, 0.5)
        if diagnosis == "A4":
            return numpy.random.normal(4, 0.5)
        if diagnosis == "B3":
            return numpy.random.normal(4, 0.5)
        if diagnosis == "B4":
            return numpy.random.normal(4, 1)
        else:
            print("Incorrect PatientType")
            return None
    if operation == "nursing":
        if diagnosis == "A1":
            return numpy.random.normal(4, 0.5)
        if diagnosis == "A2":
            return numpy.random.normal(8, 2)
        if diagnosis == "A3":
            return numpy.random.normal(16, 2)
        if diagnosis == "A4":
            return numpy.random.normal(16, 2)
        if diagnosis == "B1":
            return numpy.random.normal(8, 2)
        if diagnosis == "B2":
            return numpy.random.normal(16, 2)
        if diagnosis == "B3":
            return numpy.random.normal(16, 4)
        if diagnosis == "B4":
            return numpy.random.normal(16, 4)
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
        complication = "true"
    else:
        complication = "false"
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
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        arrivalTime = request.forms.get('arrivalTime')#TODO vielleicht hochzählen
        appointment = request.forms.get('appointment')
        taskRole = request.forms.get('taskRole')
        callbackURL = request.headers['CPEE-CALLBACK']

        #patients admission case without queue
        print(taskRole)
        if taskRole == "patientAdmission":

            #Give PatientId if there is no
            if not patientId:
                patientId = insert_patient(arrivalTime, patientType)
            else:
                pass

            #check if resources are available if patient has appointment
            print(appointment)
            if appointment:           
                if get_resource_amount("intake", appointment) > 0 and surgeryQueue < 2 and nursingQueue < 2:
                    intake = True
                else:
                    intake = False
            else:
                intake = False

            return {"patientType": patientType, "patientId": patientId,
                    "intake": intake}
        elif taskRole == "releasing":
            # request patient data
            set_process_status(patientId , True)
            return {"patientType": patientType, "patientId": patientId}
        else:
            data = {"patientId": patientId,
                    "patientType": patientType,
                    "arrivalTime": arrivalTime,
                    "appointment": appointment,
                    "taskRole": taskRole,
                    "callbackURL": callbackURL}
            taskQueue.put((appointment, data))
            print(taskQueue.qsize())


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
        print("Ich arbeite")
        time.sleep(20)
        task = taskQueue.get()
        patientId = task[1]['patientId']
        patientType = task[1]['patientType']
        arrivalTime = task[1]['arrivalTime']
        appointment = task[1]['appointment']
        taskRole = task[1]['taskRole']
        callbackURL= task[1]['callbackURL']
        #print(taskQueue.get()[1]['callbackURL'])

        if taskRole == "intake":
            pass
        elif taskRole == "surgery":
            pass
        elif taskRole == "nursing":
            pass
        elif taskRole == "ERTreatment":
            pass
        else:
            pass

        # Prepare the callback response as JSON
        callback_response = {
            'task_id': 'task_id',
            'status': 'completed',
            'result': {'success': True}
        }

        # Prepare the headers
        headers = {
            'content-type': 'application/json',
            'CPEE-CALLBACK': 'true'
        }

        # Send the callback response as a JSON payload
        requests.put(callbackURL, headers=headers, json=callback_response)
        print(f"PUT request sent to callback_url: {callbackURL}")


threading.Thread(target=worker, daemon=True).start()

@route('/replanPatient', method = 'POST')#TODO Implement reasonable logic for replanning
def replan_patient():
    try:
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        arrivalTime = request.forms.get('arrivalTime')

        #simply replan for the next day
        appointment = arrivalTime + 24 * 60

        #prepare data
        data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + str(patientType)+ "\",\"patientId\":\"" + str(patientId) + "\", \"arrivalTime\":\"" + str(arrivalTime) + "\",\"appointment\":\"" + str(appointment) + "\"}"
            }
        
        response = requests.post("https://cpee.org/flow/start/url/", data = data)
        print(response.forms.get('CPEE-INSTANCE'))
        return {"patientType": patientType, "patientId": patientId}

    except Exception as e:
        response.status = 500
        return {"error": str(e)}
    

run(host='::1', port=48904)
