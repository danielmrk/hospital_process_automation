from abc import ABC, abstractmethod
import random
from collections import deque, namedtuple


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

    def __init__(self):
        self.planner_helper = None
            # Definiere eine Struktur für Patienteninformationen
        self.Patient = namedtuple('Patient', ['id', 'type', 'time'])

        # Beispielhafte Ressourcen (z.B. Anzahl der verfügbaren Behandlungszimmer)
        self.max_resources = 5
    
    def set_planner_helper(self, planner_helper):
        self.planner_helper = planner_helper

    # Erstelle eine initiale Planung
    def initial_schedule(self, patients):
        # Die initiale Planung verteilt Patienten zufällig
        schedule = []
        for resource in range(self.max_resources):
            assigned_patients = random.sample(patients, len(patients) // self.max_resources)
            schedule.append(assigned_patients)
            patients = [p for p in patients if p not in assigned_patients]
        return schedule

    # Bewertungsfunktion, z.B. Minimierung der Wartezeit
    def evaluate_schedule(schedule):
        total_time = 0
        for resource in schedule:
            time = 0
            for patient in resource:
                time += patient.time
            total_time += time
        return total_time

    # Nachbarschaftsfunktion, die eine neue Planung generiert
    def get_neighbors(schedule):
        neighbors = []
        for i in range(len(schedule)):
            for j in range(i+1, len(schedule)):
                if schedule[i] and schedule[j]:
                    new_schedule = [list(row) for row in schedule]
                    patient_to_swap = random.choice(new_schedule[i])
                    new_schedule[i].remove(patient_to_swap)
                    new_schedule[j].append(patient_to_swap)
                    neighbors.append(new_schedule)
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



    @abstractmethod
    def plan(self, plannable_elements, simulation_time):
        '''
        The method that must be implemented for planning.
        :param plannable_elements: A dictionary with case_id as key and a list of element_labels that can be planned or re-planned.
        :param simulation_time: The current simulation time.
        :return: A list of tuples of how the elements are planned. Each tuple must have the following format: (case_id, element_label, timestamp).
        '''
        
        pass


    def report(self, case_id, element, timestamp, resource, lifecycle_state):
        '''
        The method that can be implemented for reporting.
        It is called by the simulator upon each simulation event.
        '''
        pass