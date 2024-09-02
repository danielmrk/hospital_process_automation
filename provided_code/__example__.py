from simulator import Simulator, EventType
from planners import Planner
from problems import HealthcareProblem
from reporter import EventLogReporter


class NaivePlanner(Planner):
    def __init__(self, eventlog_file, data_columns):
        super().__init__()
        self.eventlog_reporter = EventLogReporter(eventlog_file, data_columns)
        self.planned_patients = set()
        self.current_state = dict() 

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
        next_plannable_time = round((simulation_time + 24) * 2 + 0.5) / 2
        for case_id, element_labels in sorted(plannable_elements.items()):
            #print(f"{case_id} - len: {len(element_labels)}")

            available_info = dict()
            available_info['cid'] = case_id
            available_info['time'] = simulation_time
            available_info['info'] = simulator.planner.planner_helper.get_case_data(case_id)
            available_info['resources'] = list(map(lambda el: dict({'cid': el[0]}, **el[1]), self.current_state.items()))
            print(available_info)
            

            ############### here you should send your data to your endpoint / use it with your planner functionality ############### 


            for element_label in element_labels:
                planned_elements.append((case_id, element_label, next_plannable_time))
        print("------------------------------------------------------------------------------------------------------------------------planning end")
        return planned_elements
    

planner = NaivePlanner("./temp/event_log.csv", ["diagnosis"])
problem = HealthcareProblem()
simulator = Simulator(planner, problem)
result = simulator.run(30*24)

print(result)
