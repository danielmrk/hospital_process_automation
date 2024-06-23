# hospital_process_automation

This Project implements a simulator in order to interact with the cpee.

## Usage

1. Start the simulator_test.py at the Lehre Server
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
The initial start for arrivalTime is 500 minutes which is approximately 8:20 AM.

## Functionality and Background

The Script uses two databases.

1. patients.db
2. resources_calender.db

The patientsDB Database can be established executing the database_calender.py.
The resources_calender database can be established using the database_calender.py.

In patientsDB every Patient is stored with an individual ID, admissionDate, patientType, totalTime and processFinished variable.
The resources_calender.db has a row for every minute of a year. In addition for every minute of the year there are the resources which are available depending on the day of the week and time (resources depend on day and working time).
The Script is now able to book resources and evaluate if there are resources available.

Every task besides replanning is handled by a endpoint which eather puts the task in a priorityQueue or answers in case of patientAdmission or releasing immediately.
The rest of the tasks is handled via an asynchronous call.
Replanning is in the moment always for 10 AM at the next day implemented.
This queue is then handled by a worker thread. This worker handles them sorted by the time they start.
If no resources are available the patient has to wait.
There is no real time, the time is just a variable of the patient.

