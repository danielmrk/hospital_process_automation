from typing import List, Tuple
import random

class Patient:
    def __init__(self, patient_id, current_time, diagnosis, treatment_duration):
        self.patient_id = patient_id
        self.current_time = current_time
        self.diagnosis = diagnosis
        self.treatment_duration = treatment_duration

class SystemState:
    def __init__(self, current_patient_id, current_treatment_start, waiting_time):
        self.current_patient_id = current_patient_id
        self.current_treatment_start = current_treatment_start
        self.waiting_time = waiting_time

def create_initial_solution(patients: List[Patient]) -> List[Tuple[int, int]]:
    # Eine einfache initiale Lösung: Behandle die Patienten in der Reihenfolge ihres Eintreffens
    solution = []
    current_time = 0
    for patient in patients:
        start_time = max(current_time, patient.current_time)
        solution.append((patient.patient_id, start_time))
        current_time = start_time + patient.treatment_duration
    return solution

def evaluate_solution(solution: List[Tuple[int, int]], patients: List[Patient]) -> int:
    total_waiting_time = 0
    for patient_id, start_time in solution:
        patient = next(p for p in patients if p.patient_id == patient_id)
        waiting_time = start_time - patient.current_time
        total_waiting_time += waiting_time
    return total_waiting_time


def get_neighbors(solution: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    neighbors = []
    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            neighbor = solution.copy()
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbors.append(neighbor)
    return neighbors


def tabu_search(patients: List[Patient], max_iterations: int, tabu_tenure: int) -> List[Tuple[int, int]]:
    current_solution = create_initial_solution(patients)
    best_solution = current_solution
    best_cost = evaluate_solution(best_solution, patients)
    
    tabu_list = []
    tabu_list_size = tabu_tenure
    
    for _ in range(max_iterations):
        neighbors = get_neighbors(current_solution)
        neighbors = [neighbor for neighbor in neighbors if neighbor not in tabu_list]
        
        if not neighbors:
            break
        
        current_solution = min(neighbors, key=lambda s: evaluate_solution(s, patients))
        current_cost = evaluate_solution(current_solution, patients)
        
        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost
        
        tabu_list.append(current_solution)
        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)
    
    return best_solution


# Beispielhafte Patientendaten
patients = [
    Patient(1, 0, "diagnosis1", 10),
    Patient(2, 5, "diagnosis2", 15),
    Patient(3, 12, "diagnosis3", 20)
]

# Tabu Search ausführen
best_schedule = tabu_search(patients, max_iterations=100, tabu_tenure=5)

# Ausgabe der besten Lösung
for patient_id, start_time in best_schedule:
    print(f"Patient {patient_id} beginnt um {start_time} Uhr")
