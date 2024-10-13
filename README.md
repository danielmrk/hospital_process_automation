# hospital_process_automation

This Project implements a simulator in order to interact with the cpee.
Simulated is an artificial hospital process.
In Addition, a patient planning mechanism is realized.
It uses an Tabu-Search algorithm for optimizing the planning of the patients.

## Usage

1. Start the simulator_test.py at the Lehre Server
3. In the instanceSpawner.py we can define the simulation time(up to one year) and the amount of patients.
2. Spawn Instances using the instanceSpawner.py

In every case if an Instance is spawned it has to come with two initial Data Elements

1. patientType
2. arrivalTime

The patientType can be:
- A1
- A2
- A3
- A4
- B1
- B2
- B3
- B4
- ER

The arrivaltime has to be given in minutes. In addition the patients have to arrive in chronological order. The global time counting starts at 0 and ends after one year.
The patients appear randomly throughout the day and are processed by the hospital simulator in chronological order.
The patient type is also randomly generated with a certain probability distribution.
The simulator works through the individual process steps of the patients if the respective hospital resources are available.
Non-emergency patients are always scheduled for one of the next days after the replanner arrives.
Emergency patients are taken in directly from the hospital.
After each simulated day, the patients to be scheduled are scheduled by the planner for the day after next according to the tabu search algorithm.
The simulator creates also a logging file (hospital.log) to be able to see what happend in the hospital.

## Functionality and Background

The main scripts are:

1. instanceSpawner.py
2. simulator_main.py
3. planner.py
4. database_patients.py

### instanceSpawner.py

The instanceSpawner.py scripts is in charge of spawning patients, which arrive at the hospital.
At the beginne we can define how many days we want to simulate and how many patients we want to spawn per day.
The script generates for each simulated day the specific patients with a random arrivaltime and a specific patientType according to some probability distribution.
Then the scripts posts a request in order to spawn a new CPEE Instance.
At the end the scripts sends 7 buffer instances to give the simulator the opportunity to simulate patients which arrive at the last day of the actual simulation, but have to be replanned.
It is realized like this, because patients arrival time is the reference for the simulation time.

### simulator_main.py

The simulator is the main script of the project and interacts with the CPEE.
It creates a server using the bottle-framework in python.
It basically uses to queues and two worker threads to process hospital tasks and replanning tasks.
For Replanning tasks it uses the implemented planner.py.

#### Script Functionality

In order to describe the script, we will go through it step by step.

Line 20 -26:
Remove the previous logging file to have a new one.

Line 28-34:
Create a Loggingfile.

A patientsDB Database can be established executing the database_calender.py. In this Da

In patientsDB every Patient is stored with an individual ID, admissionDate, patientType, totalTime and processFinished variable.
The resources_calender.db has a row for every minute of a year. In addition for every minute of the year there are the resources which are available depending on the day of the week and time (resources depend on day and working time).
The Script is now able to book resources and evaluate if there are resources available.

Every task besides replanning is handled by a endpoint which eather puts the task in a priorityQueue or answers in case of patientAdmission or releasing immediately.
The rest of the tasks is handled via an asynchronous call.
Replanning is in the moment always for 10 AM at the next day implemented.
This queue is then handled by a worker thread. This worker handles them sorted by the time they start.
If no resources are available the patient has to wait.
There is no real time, the time is just a variable of the patient.

