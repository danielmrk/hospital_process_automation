#! /usr/bin/python3
from bottle import  route, run, template, request, response
import sqlite3
import requests
import numpy
import json
from datetime import datetime
import queue
import time
import random

q_nursing = queue.Queue()
q_surgery = queue.Queue()
q_ERTreatment = queue.Queue()


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

def update_resource_amount(resource_name, new_amount):
    conn = sqlite3.connect('resources.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE resources
        SET amount = ?
        WHERE resource_name = ?
    ''', (new_amount, resource_name))
    conn.commit()
    conn.close()

def update_calender(new_amount, resource_name, hour):
    conn = sqlite3.connect('calender.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE resources
        SET ? = ?
        WHERE resource_name = ?
    ''', (new_amount, resource_name, hour))
    conn.commit()

def get_resource_amount(resource_name):
    conn = sqlite3.connect('resources.db')
    cursor = conn.cursor()

    # Abfrage ausführen
    cursor.execute('''
        SELECT amount FROM resources
        WHERE resource_name = ?
    ''', (resource_name,))

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


@route('/patientAdmission', method = 'POST')
def patient_admission():
    try:
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        timeslot = request.forms.get('timeslot')
        admission_time = request.forms.get('admission_time')#TODO vielleicht hochzählen
    
        #Give PatientId if there is no
        if not patientId:
            patientId = insert_patient(admission_time, patientType)
        else:
            pass

        #if patient is not planned replan in every case
        if not timeslot:
            timeslot = False
        else:
            pass

        #Give back the resources according to patient type
        ER_resource_amount = get_resource_amount("EmergencyDep")
        intake_resource_amount = get_resource_amount("Intake")

        #Treatment is infeasible either if more than two patients have finished the intake,
        #but have not yet been processed in the Surgery or Nursing departments, or when all Intake
        #resources are occupied upon a patient's arrival.
        if intake_resource_amount < 1:
            resources_unavailable = True
        elif q_nursing.qsize() > 2 or q_surgery.qsize() > 2:
             resources_unavailable = True
        else:
            resources_unavailable = False

        #send back the required information
        return {"patientType": patientType, "patientId": patientId,
         "ER_resource_amount": ER_resource_amount,
         "timeslot": timeslot,
         "resources_unavailable": resources_unavailable}

    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}

@route('/replanPatient', method = 'POST')#TODO Implement reasonable logic for replanning
def replan_patient():
    try:
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')
        timeslot = request.forms.get('timeslot')
        data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + str(patientType)+ "\",\"patientId\":\"" + str(patientId) + "\", \"timeslot\":\"" + str(timeslot) + "\"}"
            }
        
        response = requests.post("https://cpee.org/flow/start/url/", data = data)
        print(response.forms.get('CPEE-INSTANCE'))
        return {"patientType": patientType, "patientId": patientId}

    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@route('/intakePatient', method = 'POST')
def intake_patient():
    try:
        #Consume a resource
        amount_intake_resource = get_resource_amount("Intake")
        if amount_intake_resource > 0:
            update_resource_amount("Intake", amount_intake_resource - 1)
            resource_consumed = True
        else:
            resource_consumed = False
            
        #request patient data
        patientType = request.forms.get('patientType')
        patientId = request.forms.get('patientId')

        #add time to total time
        patientTime = get_patient_time(patientId)
        intake_duration = numpy.random.normal(1,0.125)
        patientTime += intake_duration
        set_patient_time(patientId, patientTime)

        #decide if patient needs surgery
        if "a" in patientType.lower():
            if "2" in patientType or "3" in patientType or "4" in patientType:
                surgery = "true"
            else:
                surgery = "false"
        elif "b" in patientType.lower():
            if "3" in patientType or "4" in patientType:
                surgery = "true"
            else:
                surgery = "false"
        else:
            surgery = "false"

        #release intake resource
        amount_intake_resource = get_resource_amount("Intake")
        if resource_consumed:
            update_resource_amount("Intake", amount_intake_resource + 1)
        return {"patientType": patientType, "patientId": patientId,
         "surgery": surgery,
         "phantomPain": "false"}


    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}

@route('/surgery', method = 'POST')
def surgery():
    try:
        #request patient data
        patientId = request.forms.get('patientId')
        patientType = request.forms.get('patientType')
        patientTime = get_patient_time(patientId)

        #wait for free resource
        q_surgery.put("patient")
        while get_resource_amount("Surgery") < 1:
            patientTime += 1
            time.sleep(1)
        q_surgery.get()
        #Consume a resource
        amount_intake_resource = get_resource_amount("Surgery")
        update_resource_amount("Surgery", amount_intake_resource - 1)
        #update patient time with treatment time
        intake_duration = calculate_operation_time(patientType[-2:], "surgery")
        patientTime += intake_duration
        set_patient_time(patientId, patientTime)

        #give resources back
        amount_intake_resource = get_resource_amount("Surgery")
        update_resource_amount("Surgery", amount_intake_resource + 1)
        return {"patientType": patientType, "patientId": patientId}


    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@route('/nursing', method = 'POST')
def nursing():
    try:
        # request patient data
        patientId = request.forms.get('patientId')
        patientType = request.forms.get('patientType')
        patientTime = get_patient_time(patientId)

        if "a" in patientType.lower():
            resourceName = "NursingA"
        if "b" in patientType.lower():
            resourceName = "NursingB"
        else:
            resourceName = "NursingA"

        #wait for free resources
        q_nursing.put("patient")
        while get_resource_amount(resourceName) < 1:
            patientTime += 1
            time.sleep(1)
        q_nursing.get()
        #consume resources
        amount_intake_resource = get_resource_amount(resourceName)
        update_resource_amount(resourceName, amount_intake_resource - 1)

        #define complications
        complication = complication_generator(patientType)

        #update patient time with treatment time
        intake_duration = calculate_operation_time(patientType[-2:], "nursing")
        patientTime += intake_duration
        set_patient_time(patientId, patientTime)

        #give resources back
        amount_intake_resource = get_resource_amount(resourceName)
        update_resource_amount(resourceName, amount_intake_resource + 1)


        return {"patientType": patientType, "patientId": patientId,
                "complication": complication}  


    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@route('/releasing', method = 'POST')
def releasing():
    try:
        # request patient data
        patientId = request.forms.get('patientId')
        patientType = request.forms.get('patientType')
        set_process_status(patientId , True)
        return {"patientType": patientType, "patientId": patientId}
    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@route('/ERTreatment', method = 'POST')
def ER_Treatment():
    try:
        #request patient data
        patientId = request.forms.get('patientId')
        patientType = request.forms.get('patientType')
        patientTime = get_patient_time(patientId)

        #Consume a resource
        #wait for free resource
        q_ERTreatment.put("ER_patient")
        while get_resource_amount("EmergencyDep") < 1:
            patientTime += 1
            time.sleep(1)
        q_ERTreatment.get()
        amount_intake_resource = get_resource_amount("EmergencyDep")
        update_resource_amount("EmergencyDep", amount_intake_resource - 1)

        #update patient time with treatment time
        intake_duration = numpy.random.normal(2,0.5)
        patientTime += intake_duration
        set_patient_time(patientId, patientTime)

        diagnosis = ER_diagnosis_generator()
        patientType = str(patientType+"-"+diagnosis)

        #decide if patient needs surgery
        if "a" in patientType.lower():
            if "2" in patientType or "3" in patientType or "4" in patientType:
                surgery = "true"
            else:
                surgery = "false"
        elif "b" in patientType.lower():
            if "3" in patientType or "4" in patientType:
                surgery = "true"
            else:
                surgery = "false"
        else:
            surgery = "false"

        #decide if patient has phantom pain
        random_number = random.random()
        if random_number > 0.5:
            phantomPain = "true"
        else:
            phantomPain = "false"

        #give resources back
        amount_intake_resource = get_resource_amount("EmergencyDep")
        update_resource_amount("EmergencyDep", amount_intake_resource + 1)
        return {"patientType": patientType, "patientId": patientId,
         "surgery": surgery,
         "phantomPain": phantomPain}


    except Exception as e:
        response.status = 500
        print(e)
        return {"error": str(e)}



run(host='::1', port=48904)
