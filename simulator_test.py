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
surgeryNursingQueue = queue.Queue()

#Amount of nursing in the queue
nursingQueue = 0

class PrioritizedItem:
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __repr__(self):
        return f'PrioritizedItem(priority={self.priority}, data={self.data})'
    
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

def update_resource_amount(resourceName, amount, startTime, endTime):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()

    # Sicherheitscheck: Prüfe den Spaltennamen
    valid_columns = ['intake', 'surgery', 'a_bed', 'b_bed', 'emergency']  # Beispiel für gültige Spaltennamen
    if resourceName not in valid_columns:
        raise ValueError("Ungültiger Spaltenname")
    
    query = f'''
        UPDATE resources
        SET {resourceName} = ?
        WHERE globalMinute >= ? AND globalMinute <= ?
    '''
    cursor.execute(query, (amount, startTime, endTime))
    conn.commit()
    conn.close()

def get_resource_amount(resource_name, time):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()

    # Sicherheitscheck: Prüfe den Spaltennamen
    valid_columns = ['intake', 'surgery', 'a_bed', 'b_bed', 'emergency']  # Beispiel für gültige Spaltennamen
    if resource_name not in valid_columns:
        raise ValueError("Ungültiger Spaltenname")
    
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
    
def get_minute_next_day(patientTime):
    conn = sqlite3.connect('resources_calender.db')
    cursor = conn.cursor()

    
    # Abfrage ausführen
    query = f'SELECT hour FROM resources WHERE globalMinute = ?'
    cursor.execute(query, (patientTime,))

    # Ergebnis abrufen (es sollte nur ein Ergebnis geben)
    result = cursor.fetchone()

    #calculate how many minutes it will take to get to next day 10 o clock
    minutes_next_day = (24 - result[0] + 10) * 60

    # Verbindung schließen
    conn.close()
    # Wenn ein Ergebnis vorhanden ist, gib die minuten zurück, sonst gib None zurück
    if result:
        return minutes_next_day 
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


        #patients admission case without queue
        if taskRole == "patientAdmission":

            #set patienttime to arrivaltime for this run
            patientTime = arrivalTime

            #Assign PatientId if there is no and put patient into patient database
            if not patientId:
                patientId = insert_patient(arrivalTime, patientType)
            else:
                pass

            #check if resources are available if patient has appointment
            print("Test:")
            print(get_resource_amount("intake", patientTime))
            print(surgeryNursingQueue.qsize())
            print(patientTime)
            if appointment:           
                if get_resource_amount("intake", patientTime) > 0 and surgeryNursingQueue.qsize() < 3:
                    intake = True
                else:
                    intake = False
            elif patientType == "ER":
                intake = True
            else:
                intake = False

            return {"patientType": patientType, "patientId": patientId, 
                    "patientTime": patientTime,
                    "intake": intake}
        elif taskRole == "releasing":
            # set patienttime to final total time in the database and set the process status to finished
            set_patient_time(patientId, (int(patientTime) - int(arrivalTime)))
            set_process_status(patientId , True)
            return {"patientType": patientType, "patientId": patientId}
        else:
            data = {"patientId": patientId,
                    "patientType": patientType,
                    "arrivalTime": arrivalTime,
                    "patientTime": patientTime,
                    "appointment": appointment,
                    "taskRole": taskRole,
                    "callbackURL": callbackURL}


            #add task to the queue to process it by the worker and prioritize it by patient time
            data = json.dumps(data)
            taskQueue.put(PrioritizedItem(int(patientTime), data))
            print(list(taskQueue.queue))

            #Queue to check how many patients are in surgery or nursing queue
            if taskRole == "surgery" or taskRole == "nursing":
                surgeryNursingQueue.put("Patient")

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
            #read out patient data out of queue
            print(list(taskQueue.queue))
            task = taskQueue.get()
            task = json.loads(task.data)
            print(task)
            patientId = task['patientId']
            patientType = task['patientType']
            arrivalTime = task['arrivalTime']
            patientTime = task['patientTime']
            appointment = task['appointment']
            taskRole = task['taskRole']
            callbackURL= task['callbackURL']

            if taskRole == "intake":

                #calculate intake duration
                intake_duration = round(numpy.random.normal(60, 7.5))

                #book resources
                amount = get_resource_amount("intake", patientTime)
                if amount > 0:
                    update_resource_amount("intake", (amount - 1), patientTime, int(patientTime) + intake_duration )
                else:
                    while get_resource_amount("intake", patientTime) < 1:
                        patientTime = int(patientTime) + 1
                        print("Waiting")
                    amount = get_resource_amount("intake", patientTime)
                    update_resource_amount("intake", (amount - 1), patientTime, int(patientTime) + intake_duration )

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
                amount = get_resource_amount("surgery", patientTime)
                if amount > 0:
                    update_resource_amount("surgery", (amount - 1), patientTime, int(patientTime) + surgeryDuration )
                else:
                    while get_resource_amount("surgery", patientTime) < 1:
                        patientTime = int(patientTime) + 1
                        print("Waiting")
                    amount = get_resource_amount("surgery", patientTime)
                    update_resource_amount("surgery", (amount - 1), patientTime, int(patientTime) + surgeryDuration )


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
                    resourceName = "a_bed"
                elif "b" in patientType.lower():
                    resourceName = "b_bed"
                else:
                    print("Error")

                #book resources
                amount = get_resource_amount(resourceName, patientTime)
                if amount > 0:
                    update_resource_amount(resourceName, (amount - 1), patientTime, int(patientTime) + nursingDuration)
                else:
                    while get_resource_amount(resourceName, patientTime) < 1:
                        patientTime = int(patientTime) + 1
                        print("Waiting")
                    amount = get_resource_amount(resourceName, patientTime)
                    update_resource_amount(resourceName, (amount - 1), patientTime, int(patientTime) + nursingDuration)


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
                amount = get_resource_amount("emergency", patientTime)
                if amount > 0:
                    update_resource_amount("emergency", (amount - 1), patientTime, int(patientTime) + ERDuration)
                else:
                    while get_resource_amount("emergency", patientTime) < 1:
                        patientTime = int(patientTime) + 1
                    amount = get_resource_amount("emergency", patientTime)
                    update_resource_amount("emergency", (amount - 1), patientTime, int(patientTime) + ERDuration)

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
            else:
                print("Ungültige Taskrole")
            taskQueue.task_done()
        except Exception as e:
            response.status = 500
            print(e)
            return {"error": str(e)}


threading.Thread(target=worker, daemon=True).start()

@route('/replanPatient', method = 'POST')#TODO Implement reasonable logic for replanning
def replan_patient():
    try:
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        arrivalTime = request.forms.get('arrivalTime')


        #simply replan for the next day update appointment and arrivaltime
        appointment = True
        arrivalTime = int(arrivalTime) + get_minute_next_day(arrivalTime)
        print("Arrivaltime:" + str(arrivalTime))
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
