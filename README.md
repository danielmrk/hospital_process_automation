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

In order to describe the script, we will go through it step by step.<br>

Line 20 -26:<br>
Remove the previous logging file to have a new one.

Line 28-34:<br>
Create a Loggingfile.

Line 37 - 88:<br>
Define the Taskqueues, the global variables, and the dayarray for resource management.
The day arrays are arrays of the length of a year in minutes and contain for each resource the resources per minute od a year. For example Intake is just available during working hours on business days.

Line 90 - 100:<br>
Define a Prioritize Item for the taskqueue.

Line 102 - 112:<br>
Define a function which inserts a new patient into the patients.db.

Line 116 - 130:<br>
Define a Function which updates the resource amount in the day array.
So we can keep track of each timeframe of the year and their resources.

Line 132 - 210:<br>
Set and get functions.

Line 211 - 226:<br>
Functions which map global minutes to a datetime and vise versa.
We start at 01/01/2018.

Line 254 - 291:<br>
Functions which calculates the operation time of a task based on the patientType and probabilities.

Line 295 - 321:<br>
Generates a complication with a given probability.

Line 324 - 344:<br>
Generates the diagnosis for ER Patients.

Line 347 - 392:<br>
This Function can be routed and is an asynchronous endpoint of the CPEE.
It puts every task, priotitized by the occured time into the queue.

Line 395 - 808:<br>
This is on of the two main worker threads in the simulation.
This worker processes chronologically the tasks sent by the CPEE.
The CPEE always send an taskrole, based on which this worker decides what to do.

In patientAdmission the worker decides if an patient is ready for intake.
Therefore the resources and the appointment of the patient is relevant.
ER Patients are always processed directly.
If the patient shows up the first time he gets an ID and is added to the database.

If the patient is now further processed in intake, surgery and nursing, the worker always simulates the time it takes, checks if the patient hast to wait, and updates the required resources in the arrays.
In some stations the worker also simulates if an patient has compliations or needs further treatment.
Also penalty is handled by the worker.
The penalty is used for the Scores to evaluate the planning algo.
If a task is processed the worker send an answer to the stored reply URL of the CPEE.
The logging function is used for monitoring the processed tasks.
If a patient is released, the worker sets the process_status in the patientDatabase to one to indicate that the patient was succesfully processed.
If the patient leaves the hospital the status is two.

Line 810 - 916<br>
This is the second worker thread which processes the petients which have to be replanned.
It takes the patients out of the taskQueueReplanning and appends them to a list.
After each day the list of patients which have to be replanned are processed by the planner.py script and are assigned to a new timeslot on the next day.
If this happens the worker spawns the new instances.

Line 918 - 926:<br>
The Threads are started and a planner instance is created.

Line 928 - 962:<br>
This Function can be routed and is an asynchronous endpoint of the CPEE.
It puts every replanning task into the taskQueueReplanning.

Line 964 - 973:<br>
This Function can be routed and is an asynchronous endpoint of the CPEE.
If the system state is requested by the CPEE this function returns the systemstate of a given minute.

### planner.py

The planner is in charge for replanning the patients.
For optimizing the scores it uses the tabu-search algorithm
Input is the list of patients which have to be replanned.
It returns the patients whith a new assigned timeslot.

#### Script Functionality

Line 24 - 49:<br>
Test

