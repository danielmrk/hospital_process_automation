from abc import ABC, abstractmethod
import random
from collections import deque, namedtuple
import os
import subprocess
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

    def __init__(self, eventlog_file, data_columns): # init the planning algo
        self.planned_patients = set()
        self.current_state = dict() 
        self.daycounter = 1
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

    def calculate_operation_time(self, diagnosis, operation): # calculate the operation time for simulating
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

    # update the resource amount of an array for simulating
    def update_resource_amount(self,dayarray , startTime, endTime, update):
        dayarray[startTime:endTime] = [update] * int(endTime - startTime)
        return dayarray

    # get the resource amount of an array for simulating
    def get_resource_amount(self, day_array, time):
        return day_array[time]

    # create a random time
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
        
        # Check if there are elements
        if len(plannable_elements) == 0:
            elements_sorted = []

        # Iteriere über die plannable_elements, um Informationen zu sammeln und das Dictionary zu erstellen
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
        
        # create local copy of the day array
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
            time_start = case['assigned_timeslot']
            time_start = int(math.floor(self.time_to_global_minutes(time_start)))

            # get the resources
            intake_amount = self.get_resource_amount(day_array_intake, time_start)

            intake_successful = False
            if intake_amount > 0: # check if resources for the planning are available

                # update the resources and set intake to successful
                intake_duration = intake_duration = round(numpy.random.normal(60, 7.5))
                day_array_intake = self.update_resource_amount(day_array_intake, time_start, time_start + intake_duration, (intake_amount - 1) )
                time_start = math.floor(time_start + intake_duration)
                intake_successful = True

            else: # else give penalty
                intake_infeasible += 3

            if intake_successful: # if intake successful continue with surgery (A2, A3, A4, B3, B4)
                if case['info']['diagnosis'] == "A2" or case['info']['diagnosis'] == "A3" or case['info']['diagnosis'] == "A4" or case['info']['diagnosis'] == "B3" or case['info']['diagnosis'] == "B4":
                    
                    # determine surgery duration and amount
                    surgery_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "surgery"))
                    surgery_amount = self.get_resource_amount(day_array_surgery, time_start)

                    if surgery_amount > 1: # if > 1 everything ok
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, time_start + surgery_duration, (surgery_amount - 1))
                        time_start = math.floor(time_start + surgery_duration)
                    elif surgery_amount == 1: # if == 1 penalty, because there are no more free spaces
                        free_spots_available += 5
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, time_start + surgery_duration, (surgery_amount - 1))
                        time_start = math.floor(time_start + surgery_duration)
                    elif surgery_amount == 0: # if == 0 waiting
                        while self.get_resource_amount(day_array_surgery, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                        free_spots_available += 5
                        waiting_time += 1 # penalty for waiting
                        amount = self.get_resource_amount(day_array_surgery, time_start)
                        day_array_surgery = self.update_resource_amount(day_array_surgery, time_start, int(time_start) + surgery_duration, (amount - 1))

                # continue with a nursing for a patients
                if case['info']['diagnosis'] == "A1" or case['info']['diagnosis'] == "A2" or case['info']['diagnosis'] == "A3" or case['info']['diagnosis'] == "A4":
                    
                    # determine duration and amount
                    nursing_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "nursing"))
                    nursing_amount = self.get_resource_amount(day_array_a_nursing, time_start)
                    if nursing_amount > 1: # if > 1 everything ok # TODO
                        day_array_a_nursing = self.update_resource_amount(day_array_a_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        time_start = math.floor(time_start + nursing_duration)
                    elif nursing_amount == 1:  # if == 1 penalty, because there are no more free spaces
                        day_array_a_nursing = self.update_resource_amount(day_array_a_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        free_spots_available += 5 # penalty that there is no space
                        time_start = math.floor(time_start + nursing_duration)
                    elif nursing_amount == 0: # if == 0 waiting
                        while self.get_resource_amount(day_array_a_nursing, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                        free_spots_available += 5 # penalty that there is no space
                        waiting_time += 1 # penalty for waiting
                        amount = self.get_resource_amount(day_array_a_nursing, time_start)
                        day_array_a_nursing = self.update_resource_amount(day_array_a_nursing, time_start, int(time_start) + nursing_duration, (amount - 1))

                # continue with b nursing for a patients
                elif case['info']['diagnosis'] == "B1" or case['info']['diagnosis'] == "B2" or case['info']['diagnosis'] == "B3" or case['info']['diagnosis'] == "B4":

                    # determine duration and amount
                    nursing_duration = math.floor(self.calculate_operation_time(case['info']['diagnosis'], "nursing"))
                    nursing_amount = self.get_resource_amount(day_array_a_nursing, time_start)
                    if nursing_amount > 1: # if > 1 everything ok # TODO
                        day_array_b_nursing = self.update_resource_amount(day_array_b_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        time_start = math.floor(time_start + nursing_duration)
                    elif nursing_amount == 1: # if == 1 penalty, because there are no more free spaces
                        day_array_b_nursing = self.update_resource_amount(day_array_b_nursing , time_start, time_start + nursing_duration, (nursing_amount - 1) )
                        free_spots_available += 5 # penalty that there is no space
                        time_start = math.floor(time_start + nursing_duration)
                    elif nursing_amount == 0: # if == 0 waiting
                        while self.get_resource_amount(day_array_b_nursing, time_start) < 1:
                            time_start = math.floor(time_start + 1)
                        free_spots_available += 5 # penalty that there is no space
                        waiting_time += 1 # penalty for waiting
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
        
        # Erzeuge Nachbarschaften durch Vertauschen der Zeitfenster zwischen zwei Patienten
        for i in range(num_patients):
            for j in range(i + 1, num_patients):
                # Erstelle eine tiefe Kopie der ursprünglichen Planung, damit die Änderungen nicht die originale Liste beeinflussen
                neighbor = copy.deepcopy(schedule)

                counter += 1

                # Vertausche die assigned_timeslot von Patient i und Patient j
                neighbor[i]['assigned_timeslot'], neighbor[j]['assigned_timeslot'] = neighbor[j]['assigned_timeslot'], neighbor[i]['assigned_timeslot']
                
                # Füge die veränderte Planung zur Nachbarschaftsliste hinzu
                neighbor_sorted = sorted(neighbor, key=lambda x: x['assigned_timeslot'])
                neighbor_dict = dict()
                neighbor_dict["ID"] = counter
                neighbor_dict["Solution"] = neighbor_sorted
                neighbors.append(neighbor_dict)
        return neighbors

    # Hauptalgorithmus
    def tabu_search(self, plannable_elements, max_iterations=3, tabu_tenure=10):
        # Initiale Lösung
        current_schedule = self.initial_schedule(plannable_elements)

        # define best schedule and best cost
        best_schedule = current_schedule
        best_cost = self.evaluate_schedule(current_schedule)

        # Tabuliste (FIFO Queue)
        tabu_list = deque(maxlen=tabu_tenure)
        
        for iteration in range(max_iterations): # iterstions for the best solution

            neighbors = self.get_neighbors(current_schedule) #get neighbors
            next_schedule = None
            next_cost = float('inf')
            
            for neighbor in neighbors: # evaluate the costs of every schedule
                cost = self.evaluate_schedule(neighbor['Solution'])
                if neighbor not in tabu_list and cost < next_cost: # update the best costs
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
                    
            #print(f"Iteration {iteration+1}: Beste Kosten = {next_cost}")
            if 'Solution' in best_schedule:
                best_schedule = best_schedule['Solution']
        
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

    def plan(self, plannable_elements):
        # define list of planned elements
        try:
            planned_elements = []

            # get the best schedule with tabu search
            best_schedule = self.tabu_search(plannable_elements)


            for case in best_schedule:

                case['assigned_timeslot'] = (self.time_to_global_hours(case['assigned_timeslot']))

                planned_elements.append((case['cid'], case['info'], case['assigned_timeslot']))

            print(planned_elements)
            return planned_elements
        except Exception as e:
            print(e)
            return {"error": str(e)}
    

planner = Planner("./temp/event_log.csv", ["diagnosis"])

