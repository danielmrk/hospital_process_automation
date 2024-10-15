# hospital_process_automation

This Project implements a simulator in order to interact with the CPEE.
Simulated is an artificial hospital process.
In addition, a patient planning mechanism is realized.
It uses an Tabu-Search algorithm for optimizing the planning of the patients.

## Usage

1. Execute the patientsDB.py if there is no database.
2. Start the simulator_main.py at the Lehre Server
3. In the instanceSpawner.py we can define the simulation time(up to one year) and the amount of patients.
4. Spawn Instances using the instanceSpawner.py

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
Non-emergency patients have always to be replanned.
Emergency patients are taken in directly from the hospital.
After each simulated day, the patients to be scheduled are scheduled by the planner for the next day, according to the tabu search algorithm.
The simulator creates also a logging file (hospital.log) to be able to see what happens in the hospital.

## Functionality and Background

The main scripts are:

1. instanceSpawner.py
2. simulator_main.py
3. planner.py
4. database_patients.py

### 1. instanceSpawner.py

The instanceSpawner.py scripts is in charge of spawning patients, which arrive at the hospital.
At the beginning we can define, how many days we want to simulate and how many patients we want to spawn per day.
The script generates for each simulated day the specific patients with a random arrivaltime and a specific patientType according to some probability distribution.
Then the scripts posts a request in order to spawn a new CPEE Instance.
At the end, the script sends 7 buffer instances to give the simulator the opportunity to simulate patients which arrive at the last day of the actual simulation, but have to be replanned.
It is realized like this, because patients arrival time is the reference for the simulation time.

### 2. simulator_main.py

The simulator is the main script of the project and interacts with the CPEE.
It creates a server using the bottle-framework in python.
It basically uses two queues and two worker-threads to process hospital tasks and replanning tasks.
For Replanning tasks it uses the implemented planner.py.

#### Script Functionality

In order to describe the script, we will go through it step by step.<br>

**Line 20 - 26:**<br>
Remove the previous logging file to have a new one.

**Line 28-34:**<br>
Create a Loggingfile.

**Line 37 - 88:**<br>
Define the Taskqueues, the global variables, and the dayarrays for resource management.
The dayarrays are arrays of the length of a year in minutes and contain for each resource an amount per minute of a year. For example Intake is just available during working hours on business days.

**Line 90 - 100:**<br>
Define a Prioritize Item for the taskqueue.

**insert_patient():**<br>
Define a function which inserts a new patient into the patients.db.

**update_resource_amount():**<br>
Define a Function which updates the resource amount in the day array.
So we can keep track of each timeframe of the year and their resources.

**Line 132 - 210:**<br>
Set and get functions.

**Line 211 - 226:**<br>
Functions which map global minutes to a datetime and vice versa.
We start at 01/01/2018.

**set_process_status():** <br>
Sets the status of a patient eather to one (successfully processed) or to two (left the hospital after 7 days).

**calculate_operation_time():**<br>
Functions which calculates the operation time of a task based on the patientType and cartain probabilities.

**complication_generator():**<br>
Generates a complication with a given probability.

**ER_diagnosis_generator():**<br>
Generates the diagnosis for ER-Patients.

**task_queue():**<br>
This Function can be routed and is an asynchronous endpoint of the CPEE.
It puts every task, priotitized by the occured time into the queue.

**worker():**<br>
This is on of the two main worker threads in the simulation.
This worker processes chronologically the tasks sent by the CPEE.
The CPEE always sends a taskrole, based on which this worker decides what to do.

In patientAdmission the worker decides if an patient is ready for intake.
Therefore the resources and the appointment of the patient is relevant.
ER-Patients are always processed directly.
If the patient shows up the first time he gets an ID and is added to the database.

If the patient is now further processed in intake, surgery and nursing, the worker always simulates the time it takes, checks if the patient has to wait, and updates the required resources in the arrays.
In some stations the worker also simulates if a patient has complications or needs further treatment.
Also penalty is handled by the worker.
The penalty is used for the scores to evaluate the planning algo.
If a task is processed the worker send an answer to the stored reply URL of the CPEE.
The logging function is used for monitoring the processed tasks.
If a patient is released, the worker sets the process_status in the patientDatabase to one to indicate that the patient was succesfully processed.
If the patient leaves the hospital the status is two.

replanning_worker():<br>
This is the second worker thread which processes the patients which have to be replanned.
It takes the patients out of the taskQueueReplanning and appends them to a list.
After each day the list of patients which have to be replanned are processed by the planner.py script and are assigned to a new timeslot on the next day.
If this happens the worker spawns the new instances.

Line 920 - 928:<br>
The Threads are started and a planner instance is created.

replan_patient():<br>
This Function can be routed and is an asynchronous endpoint of the CPEE.
It puts every replanning task into the taskQueueReplanning.

get_system_state():<br>
This Function can be routed and is an synchronous endpoint of the CPEE.
If the system state is requested by the CPEE this function returns the systemstate of a given minute.

### 3. planner.py

The planner is in charge for replanning the patients.
For optimizing the scores it uses the tabu-search algorithm
Input is the list of patients which have to be replanned.
It returns the patients whith a new assigned timeslot.

#### Script Functionality

**Line 24 - 49:**<br>
Here The Planner instance initializes its self. variables.
It creates dayarrays, daycounter and control variables.
The day arrays are arrays of the length of two days in minutes and contain for each resource an amount per minute of the day. For example Intake is just available during working hours.

**Line 53 - 90:**<br>
Function which calculates the operation time of a task based on the patientType and probabilities.

**Line 92 - 99:**<br>
Get and set the resource amount of the dayarray.

**random_time():** <br>
Create a Random Time between 08:00 and 17:00 for the initial schedule of the tabu search algo.

**initial_schedule():** <br>
Create an initial schedule. This is the reference for the tabu search algorithm in terms of neighborhood and cost function.
In this function, every patient is assigned to a random time throughout the day.

**evaluate_schedule():** <br>
This function is in charge of evaluation a planning and assign it to a certain cost.
The function simulates the planning into a timeframe of two days similar to the simulator script.
Each time a patient has to wait, no resources for ER-Patients are available or intake is not possible, the function counts up a cost.
This cost is returned at the end, and serves for evaluating the different neighbors of the initial schedule.

**get_neighbors():** <br>
This function searches for a given schedule the neighbors of this schedule.
To do this, it swaps various patients.
It returns a list with different schedule approaches.

**tabu_search():** <br>
This function implements the Tabu Search algorithm to find an optimized schedule from a set of plannable elements. It begins with an initial solution and iterates to improve it by exploring neighboring solutions. The algorithm avoids revisiting recently explored solutions by using a tabu list with a defined tenure, ensuring better exploration of the solution space. During each iteration, the best neighboring solution is selected, and if it improves the overall cost, it updates the current best schedule. After the specified number of iterations, the best-found schedule is returned

**stunden_in_wochentag():** <br>
This function converts the number of hours passed since January 1, 2018, into the corresponding day of the week. It calculates the target date and returns the weekday as a string (e.g., "Monday" or "Tuesday")

**next_business_day():** <br>
This function returns the next business day. For example, for friday, it will return monday.

**Line 348 - 364:** <br>
Functions which map datetime.time to a minutes and hours.

**plan():** <br>
The plan function is called by the simulator_main.py.
It uses the tabu_search function to convert the plannable elements to planned elements and return them.


### 4. database_patients.py

This function establishes a connection to an SQLite database and creates a table named patients if it doesn't already exist. The table includes columns for storing patient information such as patientID, admissionDate, patientType, arrivalTime, totalTime, and a processFinished flag. The changes are committed to the database after the table creation.

In the database are stored all patients, and their parameters.
