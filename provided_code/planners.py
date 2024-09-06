from abc import ABC, abstractmethod
import random
from collections import deque, namedtuple
import os
import subprocess
from simulator import Simulator, EventType
from problems import HealthcareProblem
from reporter import EventLogReporter
import math
import datetime
import copy


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
        self.eventlog_reporter = EventLogReporter(eventlog_file, data_columns)
        self.planned_patients = set()
        self.current_state = dict() 
        self.daycounter = 0
        self.planner_helper = None
        # Definiere eine Struktur für Patienteninformationen
        self.Patient = namedtuple('Patient', ['id', 'type', 'time'])

        # Beispielhafte Ressourcen (z.B. Anzahl der verfügbaren Behandlungszimmer)
        self.max_resources = 5

        # Datei löschen
        datei_zum_loeschen = "planning_tabu_calender.db"
        if os.path.exists(datei_zum_loeschen):
            os.remove(datei_zum_loeschen)
            print(f"{datei_zum_loeschen} wurde gelöscht.")
        else:
            print(f"{datei_zum_loeschen} existiert nicht.")

        # Datei über die Kommandozeile ausführen
        datei_zum_ausfuehren = "database.py"
        try:
            subprocess.run(["python3", datei_zum_ausfuehren], check=True)
            print(f"{datei_zum_ausfuehren} wurde erfolgreich ausgeführt.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen von {datei_zum_ausfuehren}: {e}")
    
    def set_planner_helper(self, planner_helper):
        self.planner_helper = planner_helper


    def random_time(self):
    # Start- und Endzeiten definieren (8:00 Uhr und 17:00 Uhr)
        start_time = datetime.datetime.strptime('08:00', '%H:%M')
        end_time = datetime.datetime.strptime('17:00', '%H:%M')
        
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
        for case_id, element_labels in sorted(plannable_elements.items()):
            available_info = dict()  # Erstelle ein Dictionary
            
            # Füge Daten zum Dictionary hinzu
            available_info['cid'] = case_id  # Fall-ID (case_id)
            available_info['info'] = simulator.planner.planner_helper.get_case_data(case_id)  # Zusätzliche Fall-Daten
            available_info['assigned_timeslot'] = self.random_time()
            # Füge das Dictionary zur Liste der Elemente hinzu
            elements.append(available_info)
            elements_sorted = sorted(elements, key=lambda x: x['assigned_timeslot'])
    
        return elements_sorted

    # Bewertungsfunktion, z.B. Minimierung der Wartezeit
    def evaluate_schedule(self, elements_sorted, schedule):
        total_time = 0
        for resource in schedule:
            time = 0
            for patient in resource:
                time += patient.time
            total_time += time
        return total_time

    # Nachbarschaftsfunktion, die eine neue Planung generiert
    def get_neighbors(self, schedule):
        neighbors = []
        
        # Anzahl der Patienten in der Planung
        num_patients = len(schedule)

        counter = 0
        print("Anzahl planungen:")
        
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
                neighbors.append(neighbor)
        return neighbors

    # Hauptalgorithmus
    def tabu_search(self, patients, max_iterations=100, tabu_tenure=10):
        # Initiale Lösung
        current_schedule = self.initial_schedule(patients)
        best_schedule = current_schedule
        best_cost = self.evaluate_schedule(current_schedule)
        
        # Tabuliste (FIFO Queue)
        tabu_list = deque(maxlen=tabu_tenure)
        
        for iteration in range(max_iterations):
            neighbors = self.get_neighbors(current_schedule)
            next_schedule = None
            next_cost = float('inf')
            
            for neighbor in neighbors:
                cost = self.evaluate_schedule(neighbor)
                if neighbor not in tabu_list and cost < next_cost:
                    next_schedule = neighbor
                    next_cost = cost
            
            # Update der aktuellen Planung
            if next_schedule:
                current_schedule = next_schedule
                tabu_list.append(current_schedule)
                
                # Update der besten Lösung
                if next_cost < best_cost:
                    best_schedule = next_schedule
                    best_cost = next_cost
                    
            print(f"Iteration {iteration+1}: Beste Kosten = {best_cost}")
        
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

    def plan(self, plannable_elements, simulation_time):
        print("------------------------------------------------------------------------------------------------------------------------planning start")
        planned_elements = []
        #print(plannable_elements.items())
        day = self.stunden_in_wochentag(simulation_time)
        #next_plannable_time = round((simulation_time + 24) * 2 + 0.5) / 2
        if day == "Montag" or day == "Dienstag" or day == "Mittwoch" or day == "Donnerstag" or day == "Sonntag":
            next_plannable_time = round((simulation_time + 24) * 2 + 0.5) / 2
        elif day == "Freitag":
            next_plannable_time = round((simulation_time + 72) * 2 + 0.5) / 2
        elif day == "Samstag":
            next_plannable_time = round((simulation_time + 72) * 2 + 0.5) / 2
        givenumber = False
        if math.floor(simulation_time)/24 > self.daycounter:
            self.daycounter += 1
            givenumber = True
        #print(self.daycounter)
        if givenumber:
            #print(len(plannable_elements))
              # Startdatum: 01.01.2018, 00:00 Uhr
            startdatum = datetime.datetime(2018, 1, 1, 0, 0)

            schedule = self.initial_schedule(plannable_elements)
            self.get_neighbors(schedule)
            
            # Datum und Uhrzeit berechnen, die den Stunden entsprechen
            zieldatum = startdatum + datetime.timedelta(hours=math.floor(simulation_time))
            #print(zieldatum)
            #print(self.stunden_in_wochentag(math.floor(simulation_time)))
        for case_id, element_labels in sorted(plannable_elements.items()):
            #print(f"{case_id} - len: {len(element_labels)}")

            available_info = dict()
            available_info['cid'] = case_id
            available_info['time'] = simulation_time
            available_info['info'] = simulator.planner.planner_helper.get_case_data(case_id)
            available_info['resources'] = list(map(lambda el: dict({'cid': el[0]}, **el[1]), self.current_state.items()))
            

            ############### here you should send your data to your endpoint / use it with your planner functionality ############### 

            if givenumber:
                for element_label in element_labels:
                    planned_elements.append((case_id, element_label, next_plannable_time))
        print("------------------------------------------------------------------------------------------------------------------------planning end")
        return planned_elements
    

planner = Planner("./temp/event_log.csv", ["diagnosis"])
problem = HealthcareProblem()
simulator = Simulator(planner, problem)
result = simulator.run(2*24)

print(result)