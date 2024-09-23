from abc import ABC, abstractmethod
import random
from collections import deque, namedtuple
import os
import subprocess
# from simulator import Simulator, EventType
# from problems import HealthcareProblem
# from reporter import EventLogReporter
import math
import datetime
import copy
import sqlite3
import numpy


class Planner(ABC):
    """
    The class that must be implemented to create a planner.
    The class must implement the plan method.
    The class must not use the simulator or the problem directly. Information from those classes is not available to it.
    The class can use the planner_helper to get information about the simulation, but only information through the planner_helper is available to it,
    other information can be constructed via the report method.
    Note that once an event is planned, it can still show up as possible event to (re)plan.
    To avoid infinite loops of planning the same event multiple times, the planner_helper.is_planned can be used to check if an event is already planned.
    """

    def __init__(self, eventlog_file, data_columns):
        #self.eventlog_reporter = EventLogReporter(eventlog_file, data_columns)
        self.planned_patients = set()
        self.current_state = dict() 
        self.daycounter = 0
        self.planner_helper = None
        # Definiere eine Struktur für Patienteninformationen
        self.Patient = namedtuple('Patient', ['id', 'type', 'time'])

        # Beispielhafte Ressourcen (z.B. Anzahl der verfügbaren Behandlungszimmer)
        self.max_resources = 5
        

                # Anzahl der Minuten pro Tag
        minutes_per_2days = 2880

        # Start- und Endminute für die Ressource (08:00 - 17:30)
        start_minute = 8 * 60  # 08:00 Uhr = 480. Minute
        end_minute = 17 * 60  # 17:30 Uhr = 1050. Minute


        # 2D-Array erstellen, globale Minute + Ressource (oder 5 außerhalb des Zeitraums)
        self.day_array_intake = [4 if start_minute <= minute <= end_minute or start_minute + 1440 <= minute <= end_minute + 1440 else 0 for minute in range(minutes_per_2days)]
        self.day_array_surgery = [5 if start_minute <= minute <= end_minute or start_minute + 1440 <= minute <= end_minute + 1440 else 1 for minute in range(minutes_per_2days)]
        self.day_array_a_nursing = [30] * 2880
        self.day_array_b_nursing = [40] * 2880
        

    
    def set_planner_helper(self, planner_helper):
        self.planner_helper = planner_helper


    def calculate_operation_time(self, diagnosis, operation):
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

    def update_resource_amount(self,dayarray , startTime, endTime, update):
        dayarray[startTime:endTime] = [update] * int(endTime - startTime)
        return dayarray

        # conn = sqlite3.connect('planning_tabu_calender.db')
        # cursor = conn.cursor()

        # # Sicherheitscheck: Prüfe den Spaltennamen
        # valid_columns = ['intake', 'surgery', 'a_bed', 'b_bed', 'emergency']  # Beispiel für gültige Spaltennamen
        # if resourceName not in valid_columns:
        #     raise ValueError("Ungültiger Spaltenname")
        
        # query = f'''
        #     UPDATE resources
        #     SET {resourceName} = ?
        #     WHERE globalMinute >= ? AND globalMinute <= ?
        # '''
        # cursor.execute(query, (amount, startTime, endTime))
        # conn.commit()
        # conn.close()

    def get_resource_amount(self, day_array, time):
        return day_array[time]

        # conn = sqlite3.connect('planning_tabu_calender.db')
        # cursor = conn.cursor()

        # # Sicherheitscheck: Prüfe den Spaltennamen
        # valid_columns = ['intake', 'surgery', 'a_bed', 'b_bed', 'emergency']  # Beispiel für gültige Spaltennamen
        # if resource_name not in valid_columns:
        #     raise ValueError("Ungültiger Spaltenname")
        
        # # Abfrage ausführen
        # query = f'SELECT {resource_name} FROM resources WHERE globalMinute = ?'
        # cursor.execute(query, (time,))

        # # Ergebnis abrufen (es sollte nur ein Ergebnis geben)
        # result = cursor.fetchone()
        
        # # Verbindung schließen
        # conn.close()
        # # Wenn ein Ergebnis vorhanden ist, gib die totalTime zurück, sonst gib None zurück
        # if result:
        #     return result[0]  # Das erste Element des Ergebnis-Tupels ist die totalTime
        # else:
        #     return None

    def random_time(self):
    # Start- und Endzeiten definieren (8:00 Uhr und 17:00 Uhr)
        start_time = datetime.datetime.strptime('08:00', '%H:%M')
        end_time = datetime.datetime.strptime('15:00', '%H:%M')
        
        # Unterschied in Sekunden berechnen
        delta = (end_time - start_time).total_seconds()
        
        # Zufällige Anzahl von Sekunden zwischen 0 und delta
        zufaellige_sekunden = random.randint(0, int(delta))
        
        # Die zufällige Zeit durch Hinzufügen der Sekunden zur Startzeit berechnen
        zufaellige_zeit = start_time + datetime.timedelta(seconds=zufaellige_sekunden)
        
        return zufaellige_zeit.time()  # Nur die Zeit ohne Datum zurückgeben

    # Erstelle eine initiale Planung
    def initial_schedule(self, plannable_elements):
        elements = []
    
    # Iteriere über die plannable_elements, um Informationen zu sammeln und das Dictionary zu erstellen
        #print(plannable_elements)
        for element in plannable_elements:
            available_info = dict()  # Erstelle ein Dictionary


            # Füge Daten zum Dictionary hinzu
            available_info['cid'] = element['cid']  # Fall-ID (case_id)
            available_info['info'] = element['info']  # Zusätzliche Fall-Daten
            available_info['assigned_timeslot'] = self.random_time()
            # Füge das Dictionary zur Liste der Elemente hinzu
            elements.append(available_info)
            elements_sorted = sorted(elements, key=lambda x: x['assigned_timeslot'])
    
        return elements_sorted

    # Bewertungsfunktion, z.B. Minimierung der Wartezeit
    def evaluate_schedule(self, elements_sorted):

        #Create databse to evaluate solutions
        # Datei löschen
        # datei_zum_loeschen = "planning_tabu_calender.db"
        # if os.path.exists(datei_zum_loeschen):
        #     os.remove(datei_zum_loeschen)
        #     print(f"{datei_zum_loeschen} wurde gelöscht.")
        # else:
        #     print(f"{datei_zum_loeschen} existiert nicht.")

        # # Datei über die Kommandozeile ausführen
        # datei_zum_ausfuehren = "database.py"
        # try:
        #     subprocess.run(["python3", datei_zum_ausfuehren], check=True)
        #     print(f"{datei_zum_ausfuehren} wurde erfolgreich ausgeführt.")
        # except subprocess.CalledProcessError as e:
        #     print(f"Fehler beim Ausführen von {datei_zum_ausfuehren}: {e}")

        day_array_intake = self.day_array_intake
        day_array_surgery = self.day_array_surgery
        day_array_a_nursing = self.day_array_a_nursing
        day_array_b_nursing = self.day_array_b_nursing



        #Define Performance Indicators
        intake_infeasible = 0
        waiting_time = 0
        free_spots_available = 0

        # Plan Schedule in the database and give penalty for bad planning
        for case in elements_sorted:
            #print(case['info']['diagnosis'])
            #print("Test" + str(case))
            time_start = case['assigned_timeslot']
            time_start = int(math.floor(self.time_to_global_minutes(time_start)))
            #print(time_start)
            intake_amount = self.get_resource_amount(day_array_intake, time_start)
            #print(intake_amount)
            intake_successful = False
            if intake_amount > 0:
                intake_duration = intake_duration = round(numpy.random.normal(60, 7.5))
                day_array_intake = self.update_resource_amount(day_array_intake, time_start, time_start + intake_duration, (intake_amount - 1) )
                time_start = math.floor(time_start + intake_duration)
                intake_successful = True
            else:
                intake_infeasible += 3
            if intake_successful:
                print(case)
                if case['info']['diagnosis'] == "A2" or case['info']['diagnosis'] == "A3" or case['info']['diagnosis'] == "A4" or case['info']['diagnosis'] == "B3" or case['info']['diagnosis'] == "B4":
                    surgery_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "surgery"))
                    surgery_amount = self.get_resource_amount(day_array_surgery, time_start)
                    if surgery_amount > 1:
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, time_start + surgery_duration, (surgery_amount - 1))
                        time_start = math.floor(time_start + surgery_duration)
                    if surgery_amount == 1:
                        free_spots_available += 1
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, time_start + surgery_duration, (surgery_amount - 1))
                    if surgery_amount == 0:
                        while self.get_resource_amount(day_array_surgery, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                            #print("Waiting")
                        free_spots_available += 1
                        waiting_time += 1
                        amount = self.get_resource_amount(day_array_surgery, time_start)
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, int(time_start) + surgery_duration, (amount - 1))
                if case['info']['diagnosis'] == "A1" or case['info']['diagnosis'] == "A2" or case['info']['diagnosis'] == "A3" or case['info']['diagnosis'] == "A4":
                    nursing_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "nursing"))
                    nursing_amount = self.get_resource_amount(day_array_a_nursing, time_start)
                    #print("nursing_amount")
                    #print(nursing_amount)
                    if nursing_amount > 0:
                        day_array_a_nursing = self.update_resource_amount(day_array_a_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        time_start = math.floor(time_start + nursing_duration)
                    if nursing_amount == 1:
                        free_spots_available += 1
                    if nursing_amount == 0:
                        while self.get_resource_amount(day_array_a_nursing, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                            #print("Waiting")
                        free_spots_available += 1
                        waiting_time += 1
                        amount = self.get_resource_amount(day_array_a_nursing, time_start)
                        day_array_a_nursing = self.update_resource_amount(day_array_a_nursing, time_start, int(time_start) + nursing_duration, (amount - 1))
                if case['info']['diagnosis'] == "B1" or case['info']['diagnosis'] == "B2" or case['info']['diagnosis'] == "B3" or case['info']['diagnosis'] == "B4":
                    nursing_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "nursing"))
                    nursing_amount = self.get_resource_amount(day_array_a_nursing, time_start)
                    #print("nursing_amount")
                    #print(nursing_amount)
                    if nursing_amount > 0:
                        day_array_b_nursing = self.update_resource_amount(day_array_b_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        time_start = math.floor(time_start + nursing_duration)
                    if nursing_amount == 1:
                        free_spots_available += 1
                    if nursing_amount == 0:
                        while self.get_resource_amount(day_array_b_nursing, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                            #print("Waiting")
                        free_spots_available += 1
                        waiting_time += 1
                        amount = self.get_resource_amount(day_array_b_nursing, time_start)
                        day_array_b_nursing = self.update_resource_amount(day_array_b_nursing, time_start, int(time_start) + nursing_duration, (amount - 1))              

        score = free_spots_available + waiting_time + intake_infeasible  
        print("Score :" + str(score))          

        return score

    # Nachbarschaftsfunktion, die eine neue Planung generiert
    def get_neighbors(self, schedule):
        neighbors = []
        
        # Anzahl der Patienten in der Planung
        num_patients = len(schedule)

        counter = 0
        #print("Anzahl planungen:")
        
        # Erzeuge Nachbarschaften durch Vertauschen der Zeitfenster zwischen zwei Patienten
        for i in range(num_patients):
            for j in range(i + 1, num_patients):
                # Erstelle eine tiefe Kopie der ursprünglichen Planung, damit die Änderungen nicht die originale Liste beeinflussen
                neighbor = copy.deepcopy(schedule)
                #print(counter)
                counter += 1
                # Vertausche die assigned_timeslot von Patient i und Patient j
                neighbor[i]['assigned_timeslot'], neighbor[j]['assigned_timeslot'] = neighbor[j]['assigned_timeslot'], neighbor[i]['assigned_timeslot']
                
                # Füge die veränderte Planung zur Nachbarschaftsliste hinzu
                neighbor_sorted = sorted(neighbor, key=lambda x: x['assigned_timeslot'])
                neighbor_dict = dict()
                neighbor_dict["ID"] = counter
                neighbor_dict["Solution"] = neighbor_sorted
                neighbors.append(neighbor_dict)
        for neighbor1 in neighbors:
            #print("Neue Solution")
            for id in neighbor1['Solution']:
                #print(id['cid'])
                pass
        if len(neighbors) < 1:
            pass
        else:
            #print(self.time_to_global_minutes(neighbors[1]['Solution'][1]['assigned_timeslot']))
            #print(neighbors[0])
            self.evaluate_schedule(neighbors[0]["Solution"])
            pass
        return neighbors

    # Hauptalgorithmus
    def tabu_search(self, plannable_elements, max_iterations=5, tabu_tenure=10):
        # Initiale Lösung
        current_schedule = self.initial_schedule(plannable_elements)
        #print("current_schedule")
        #print(current_schedule)
        best_schedule = current_schedule
        best_cost = self.evaluate_schedule(current_schedule)
        #print("Initial Schedule tested")
        # Tabuliste (FIFO Queue)
        tabu_list = deque(maxlen=tabu_tenure)
        
        for iteration in range(max_iterations):
            neighbors = self.get_neighbors(current_schedule)
            print("neighbors")
            if len(neighbors) > 0:
                #print(neighbors)
                pass
            next_schedule = None
            next_cost = float('inf')
            
            for neighbor in neighbors:
                cost = self.evaluate_schedule(neighbor['Solution'])
                if neighbor not in tabu_list and cost < next_cost:
                    next_schedule = neighbor
                    next_cost = cost

            # Update der aktuellen Planung
            if next_schedule:
                current_schedule = next_schedule['Solution']
                tabu_list.append(current_schedule)
                
                # Update der besten Lösung
                if next_cost < best_cost:
                    best_schedule = next_schedule
                    best_cost = next_cost
                    
                print(f"Iteration {iteration+1}: Beste Kosten = {next_cost}")
        
        return best_schedule

    def stunden_in_wochentag(self, stunden_seit_start):
        """
        Wandelt die Anzahl der Stunden seit dem 01.01.2018 in den Wochentag um.

        :param stunden_seit_start: Die Anzahl der Stunden seit dem 01.01.2018, 00:00 Uhr.
        :return: Der Wochentag (als String).
        """
        # Startdatum: 01.01.2018, 00:00 Uhr
        startdatum = datetime.datetime(2018, 1, 1, 0, 0)
        
        # Datum und Uhrzeit berechnen, die den Stunden entsprechen
        zieldatum = startdatum + datetime.timedelta(hours=stunden_seit_start)
        
        # Wochentag herausfinden (Montag = 0, Sonntag = 6)
        wochentag_nummer = zieldatum.weekday()
        
        # Wochentag in einen String umwandeln
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        wochentag = wochentage[wochentag_nummer]
        #print("Wochentag : " + wochentag)
        return wochentag
    
    def next_business_day(self, day):
        if day == "Montag":
            return "Dienstag"
        if day == "Dienstag":
            return "Mittwoch"
        if day == "Mittwoch":
            return "Donnerstag"
        if day == "Donnerstag":
            return "Freitag"
        if day == "Freitag":
            return "Montag"
        if day == "Samstag":
            return "Montag"
        if day == "Sonntag":
            return "Montag"

    def time_to_global_minutes(self, t):
        """
        Wandelt ein datetime.time-Objekt in globale Minuten seit Mitternacht um.
        
        :param t: Ein datetime.time-Objekt
        :return: Anzahl der Minuten seit Mitternacht
        """
        return t.hour * 60 + t.minute + t.second / 60
    
    def time_to_global_hours(self, t):
        """
        Wandelt ein datetime.time-Objekt in globale Minuten seit Mitternacht um.
        
        :param t: Ein datetime.time-Objekt
        :return: Anzahl der Minuten seit Mitternacht
        """
        return t.hour + t.minute / 60 + t.second / (60*60)

    def report(self, case_id, element, timestamp, resource, lifecycle_state):
        if((lifecycle_state != EventType.CASE_ARRIVAL) and (lifecycle_state != EventType.COMPLETE_CASE)):
            
            #######################
            #print(f"{case_id} - {timestamp} - {element.label.value} - {resource} - {lifecycle_state}")
            if(lifecycle_state == EventType.ACTIVATE_TASK):
                #print(f"activating - {element.label.value}")
                self.current_state[case_id] = {'cid': case_id, 'task': element.label.value, 'start': timestamp, 'info': simulator.planner.planner_helper.get_case_data(case_id), 'wait': True}
            elif(lifecycle_state == EventType.START_TASK):
                #print(f"activating - {element.label.value}")
                self.current_state[case_id]['wait'] = False
                self.current_state[case_id]['info'] = simulator.planner.planner_helper.get_case_data(case_id)
            elif(lifecycle_state == EventType.COMPLETE_TASK):
                #print(f"completing - {element.label.value}")
                if(self.current_state[case_id]['task'] == element.label.value):
                    self.current_state.pop(case_id)
                else:
                    #print('complete not compatible with activate/start')
                    pass
            else:
                #print("no change in state")
                pass
            
            #print(self.current_state)
            #######################


        self.eventlog_reporter.callback(case_id, element, timestamp, resource, lifecycle_state)

    def plan(self, plannable_elements):
        #print("------------------------------------------------------------------------------------------------------------------------planning start")
        #print(plannable_elements)

        #extract hours
        #simulation_time = plannable_elements['time'] 

            #print("test")
        planned_elements = []
        planned_elements_test = []
        #print(simulation_time)
        #print(simulation_time)
        # day = self.stunden_in_wochentag(simulation_time)
        # next_plannable_time = round((simulation_time + 24) * 2 + 0.5) / 2
        # if day == "Montag" or day == "Dienstag" or day == "Mittwoch" or day == "Donnerstag" or day == "Sonntag":
        #     next_plannable_time = round((simulation_time + 24) * 2 + 0.5) / 2
        # elif day == "Freitag":
        #     next_plannable_time = round((simulation_time + 72) * 2 + 0.5) / 2
        # elif day == "Samstag":
        #     next_plannable_time = round((simulation_time + 72) * 2 + 0.5) / 2
        #print(self.daycounter)
            #print(len(plannable_elements))
              # Startdatum: 01.01.2018, 00:00 Uhr
        startdatum = datetime.datetime(2018, 1, 1, 0, 0)

        best_schedule = self.tabu_search(plannable_elements)
        # #print("best_schedule")
        # #print(best_schedule)

        for case in best_schedule:
            #print("Test")
            #print(case)
            case['assigned_timeslot'] = (self.time_to_global_hours(case['assigned_timeslot']))
            print(case['cid'])
            print(case['assigned_timeslot'])
            #planned_elements.append((case['cid'], case['label'][0], case['assigned_timeslot']))
            planned_elements.append((case['cid'], case['assigned_timeslot']))

            # print("best_schedule :")
            # print(best_schedule)
            # print("plannable elements")
            # print(plannable_elements)
            #print(best_schedule)
            #schedule = self.initial_schedule(plannable_elements)
            #self.get_neighbors(schedule)
            #print(best_schedule[0])
            # Datum und Uhrzeit berechnen, die den Stunden entsprechen
        #zieldatum = startdatum + datetime.timedelta(hours=math.floor(simulation_time))
            #print(zieldatum)
            #print(self.stunden_in_wochentag(math.floor(simulation_time)))
        # for case_id, element_labels in sorted(plannable_elements.items()):
        #     print(f"{case_id} - len: {len(element_labels)}")

        #     available_info = dict()
        #     available_info['cid'] = case_id
        #     available_info['time'] = simulation_time
        #     available_info['info'] = simulator.planner.planner_helper.get_case_data(case_id)
        #     available_info['resources'] = list(map(lambda el: dict({'cid': el[0]}, **el[1]), self.current_state.items()))
            
        #     print("Test:")
        #     print(available_info['resources'])
            ############### here you should send your data to your endpoint / use it with your planner functionality ############### 

            # if givenumber:
            #     #print("Elementlabel ")
            # for element_label in element_labels:
            #     #int(element_label)
            #     planned_elements.append((case_id, element_label, next_plannable_time))
        #print("------------------------------------------------------------------------------------------------------------------------planning end")
        print(planned_elements)
        return planned_elements
    

planner = Planner("./temp/event_log.csv", ["diagnosis"])
# problem = HealthcareProblem()
# simulator = Simulator(planner, problem)
# result = simulator.run(10*24)
