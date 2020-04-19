import random
import copy
import pprint
import json

with open('process_config.json','r') as f:
    process_config = json.load(f)


from collections import deque

PRIORITY_RANGE_MIN = 1

PRIORITY_RANGE_MAX = 10

BURST_TIME_RANGE_MAX = 10

BURST_TIME_RANGE_MIN = 1

ARRIVAL_TIME_RANGE_MIN = 0

ARRIVAL_TIME_RANGE_MAX = 10

MAX_SIMULATION_TIME = 999

SIMULATION_SPEED = 1

NUMBER_OF_PROCESSES = 10

TIME_QUANTUM = 3

FIRST_COME_FIRST_SERVE = 'First Come First Serve'

SHORTEST_JOB_FIRST = 'Shortest Job First'

SHORTEST_REMAINING_TIME_FIRST = 'Shortest Remaining Time First'

ROUND_ROBIN = 'Round Robin'

PRIORITY_SCHEDULING = 'Priority Scheduling'

RESULTS = {}

GANTT = {}

ALGORITHMS = [FIRST_COME_FIRST_SERVE,
              SHORTEST_JOB_FIRST,
              SHORTEST_REMAINING_TIME_FIRST,
              ROUND_ROBIN,
              PRIORITY_SCHEDULING]


class CPU:
    def __init__(self):
        self.process = None

    def ingest_process(self, process):
        self.process = process

    def is_process_complete(self):
        if self.process is None:
            return True

        if self.process.remaining_burst_time <= 0:
            return True

        return False

    def decrement_process(self):
        if self.process is not None:
            self.process.remaining_burst_time -= 1

    def record_process_start_time(self, time):
        if self.process is not None:
            if self.process.burst_time == self.process.remaining_burst_time:
                self.process.start_time = time

    def record_process_finish_time(self, time):
        if self.process is not None:
            if self.process.finished is not True and self.process.remaining_burst_time == 0:
                self.process.finish_time = time
                self.process.finished = True

    def record_gantt(self, algorithm):

        if self.process is None:  # CPU not processing anything at this time instance
            pid = None
        else:
            pid = self.process.pid

        if algorithm in GANTT:
            GANTT[algorithm].append(pid)
        else:
            GANTT[algorithm] = [pid]

    def reset(self):
        self.process = None


class Process:
    def __init__(self, pid,random_generation):
        self.pid = pid
        self.arrival_time = 0
        self.burst_time = 0
        self.remaining_burst_time = 0
        self.priority = 0
        self.start_time = 0
        self.finish_time = 0

        self.finished = False
        self.setup(random_generation)
    
    def get_values(self,random_generation):
        if random_generation:
            return [int(random.uniform(ARRIVAL_TIME_RANGE_MIN, ARRIVAL_TIME_RANGE_MAX)),int(random.uniform(PRIORITY_RANGE_MIN, PRIORITY_RANGE_MAX)),int(random.uniform(BURST_TIME_RANGE_MIN, BURST_TIME_RANGE_MAX))]
        else: 
            return [int(process_config[self.pid-1]['arrival_time']),int(process_config[self.pid-1]['priority']),int(process_config[self.pid-1]['burst_time'])]
    
    def setup(self,random_generation):
        values = self.get_values(random_generation)
        self.arrival_time = values[0]
        self.priority = values[1]
        self.burst_time = values[2]
        self.remaining_burst_time = self.burst_time


class Simulation():
    def __init__(self,random_generation):
        self.process_pool = set()
        self.setup(random_generation)

    def setup(self,random_generation):
        # Generate Process instances and add them to the pool
        # pid is assigned sequentially
        for pid in range(1, NUMBER_OF_PROCESSES + 1):
            self.process_pool.add(Process(pid,random_generation))

    def pprint_process_pool(self):
        processes = sorted(self.process_pool)
        for process in processes:
            print 'pid %s: Arrival time: %s, Burst Time: %s, Prio: %s, remainingburst: %s' % (
                process.pid, process.arrival_time, process.burst_time, process.priority, process.remaining_burst_time)

    @classmethod
    def determine_simulation_time(self):
        """ Determines the simulation time based on the latest None in GANTT chart"""

        assert len(GANTT) != 0, 'GANTT chart is not populated yet'
        indicies = []

        for algorithm in GANTT:
            # Counting backwards in GANTT for each algorithm
            for i, x in reversed(list(enumerate(GANTT[algorithm]))):
                if x is not None:  # If None value reached
                    indicies.append(i + 1)

        return max(indicies)


class Algorithm():
    def __init__(self):
        pass

    def check_process_arrivals(self, time):
        """ Add process to deque the process if arrival time matches current time """

        for process in self.simulation.process_pool:
            if time == process.arrival_time:
                self.deque.append(process)

    def calculate_results(self):
        total_waiting_time = 0
        total_turnaround_time = 0

        for process in self.simulation.process_pool:
            waiting_time = process.start_time - process.arrival_time
            turnaround_time = process.finish_time - process.arrival_time

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time

            if self.name in RESULTS:
                RESULTS[self.name].update({
                    process.pid: {
                        'waiting_time': waiting_time,
                        'turnaround_time': turnaround_time,
                        'arrival_time': process.arrival_time,
                        'burst_time': process.burst_time,
                        'priority': process.priority,
                        'start_time': process.start_time,
                        'finish_time': process.finish_time
                    }
                })
            else:
                RESULTS[self.name] = {
                    process.pid: {
                        'waiting_time': waiting_time,
                        'turnaround_time': turnaround_time,
                        'arrival_time': process.arrival_time,
                        'burst_time': process.burst_time,
                        'priority': process.priority,
                        'start_time': process.start_time,
                        'finish_time': process.finish_time,
                    }
                }

        RESULTS[self.name].update({
            'average_waiting_time': round(float(total_waiting_time) / NUMBER_OF_PROCESSES, 2),
            'average_turnaround_time': round(float(total_turnaround_time) / NUMBER_OF_PROCESSES, 2),
        })


class FirstComeFirstServe(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = FIRST_COME_FIRST_SERVE
        self.simulation = copy.deepcopy(simulation)
        self.deque = deque()

    def get_first_process(self):
        try:
            return self.deque.popleft()
        except Exception, e:
            return  # noop


class ShortestJobFirst(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = SHORTEST_JOB_FIRST
        self.simulation = copy.deepcopy(simulation)
        self.deque = deque()

    def remove_expired_jobs_from_pool(self):
        try:
            for process in self.deque:
                if process.remaining_burst_time <= 0:
                    self.deque.remove(process)
        except Exception, e:
            return  # noop

    def get_shortest_job_from_pool(self):
        """ Returns the process with the shortest burst time """
        shortest_process = None
        shortest_process_pid_time = 999
        try:
            for process in self.deque:
                if process.burst_time < shortest_process_pid_time:
                    shortest_process = process
                    shortest_process_pid_time = process.burst_time

            return shortest_process
        except IndexError, e:
            return  # noop


class ShortestRemainingTimeFirst(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = SHORTEST_REMAINING_TIME_FIRST
        self.simulation = copy.deepcopy(simulation)
        self.deque = deque()

    def remove_expired_jobs_from_pool(self):
        try:
            for process in self.deque:
                if process.remaining_burst_time <= 0:
                    self.deque.remove(process)
        except Exception, e:
            return  # noop

    def get_shortest_remaining_time_from_pool(self):
        """ Returns the process with the shortest remaining burst time """
        shortest_remaining_burst_time_process = None
        shortest_process_pid_remaining_burst_time = 999
        try:
            for process in self.deque:
                if process.remaining_burst_time < shortest_process_pid_remaining_burst_time:
                    shortest_remaining_burst_time_process = process
                    shortest_process_pid_remaining_burst_time = process.remaining_burst_time

            return shortest_remaining_burst_time_process
        except IndexError, e:
            return  # noop


class RoundRobin(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = ROUND_ROBIN
        self.simulation = copy.deepcopy(simulation)
        self.current_round_robin_process_index = 0
        self.deque = deque()

    def get_current_process(self):
        return self.deque[self.current_round_robin_process_index]

    def get_next_process(self):
        """ Returns the process in the job pool - round robin style """

        index = self.current_round_robin_process_index
        count = 0
        try:
            while count < len(self.deque):
                if index + 1 == len(self.deque):
                    index = 0
                else:
                    index += 1

                count += 1

                # Do not return finished processes
                if self.deque[index].remaining_burst_time <= 0:
                    continue

                self.current_round_robin_process_index = index
                return self.deque[index]

        except Exception, e:
            print e
            return  # noop


class PriorityScheduling(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = PRIORITY_SCHEDULING
        self.simulation = simulation
        self.deque = deque()

    def remove_expired_jobs_from_pool(self):
        try:
            for process in self.deque:
                if process.remaining_burst_time <= 0:
                    self.deque.remove(process)
        except Exception, e:
            return  # noop

    def get_lowest_priority_from_pool(self):
        """ Returns the process with the lowest priority from pool """
        lowest_priority_process = None
        lowest_priority = 999
        try:
            for process in self.deque:
                if process.priority < lowest_priority:
                    lowest_priority_process = process
                    lowest_priority = process.priority

            return lowest_priority_process
        except Exception, e:
            return  # noop


def run_simulation(priority_range_max=PRIORITY_RANGE_MAX, burst_time_range_max=BURST_TIME_RANGE_MAX,
                   arrival_time_range_max=ARRIVAL_TIME_RANGE_MAX, time_quantum=TIME_QUANTUM,
                   number_of_processes=NUMBER_OF_PROCESSES,random_generation=True):
    global NUMBER_OF_PROCESSES
    NUMBER_OF_PROCESSES = number_of_processes if random_generation else len(process_config)

    global PRIORITY_RANGE_MAX
    PRIORITY_RANGE_MAX = priority_range_max

    global BURST_TIME_RANGE_MAX
    BURST_TIME_RANGE_MAX = burst_time_range_max

    global ARRIVAL_TIME_RANGE_MAX
    ARRIVAL_TIME_RANGE_MAX = arrival_time_range_max

    global TIME_QUANTUM
    TIME_QUANTUM = time_quantum

    global GANTT
    GANTT = {}

    simulation = Simulation(random_generation)
    cpu = CPU()

    ''' First Come First Serve '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    FCFS = FirstComeFirstServe(simulation)

    for time in range(0, MAX_SIMULATION_TIME):
        FCFS.check_process_arrivals(time)

        #  Non-premptive algorithm
        if cpu.is_process_complete():
            cpu.ingest_process(FCFS.get_first_process())

        cpu.record_process_start_time(time)
        cpu.decrement_process()
        cpu.record_process_finish_time(time)
        cpu.record_gantt(FCFS.name)

    ''' Shortest Job First '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    SJF = ShortestJobFirst(simulation)

    for time in range(0, MAX_SIMULATION_TIME):
        SJF.check_process_arrivals(time)
        SJF.remove_expired_jobs_from_pool()

        #  Non-premptive algorithm
        if cpu.is_process_complete():
            cpu.ingest_process(SJF.get_shortest_job_from_pool())

        cpu.record_process_start_time(time)
        cpu.decrement_process()
        cpu.record_process_finish_time(time)
        cpu.record_gantt(SJF.name)

    ''' Shortest Remaining Time First '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    SRTF = ShortestRemainingTimeFirst(simulation)

    for time in range(0, MAX_SIMULATION_TIME):
        SRTF.check_process_arrivals(time)
        SRTF.remove_expired_jobs_from_pool()

        cpu.ingest_process(SRTF.get_shortest_remaining_time_from_pool())
        cpu.record_process_start_time(time)
        cpu.decrement_process()
        cpu.record_process_finish_time(time)
        cpu.record_gantt(SRTF.name)

    ''' Round Robin '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    RR = RoundRobin(simulation)

    current_time_quantum = 0
    current_process = None
    for time in range(0, MAX_SIMULATION_TIME):
        RR.check_process_arrivals(time)

        if current_process is None or current_time_quantum >= TIME_QUANTUM or current_process.remaining_burst_time == 0:
            current_process = RR.get_next_process()
            current_time_quantum = 0
        else:
            current_process = RR.get_current_process()

        cpu.ingest_process(current_process)
        cpu.record_process_start_time(time)
        cpu.decrement_process()
        cpu.record_process_finish_time(time)
        cpu.record_gantt(RR.name)

        current_time_quantum += 1

    ''' Priority Scheduling '''

    cpu.reset()  # Reset cpu for next algorithm simulation
    PS = PriorityScheduling(simulation)

    for time in range(0, MAX_SIMULATION_TIME):
        PS.check_process_arrivals(time)
        PS.remove_expired_jobs_from_pool()

        cpu.ingest_process(PS.get_lowest_priority_from_pool())
        cpu.record_process_start_time(time)
        cpu.decrement_process()
        cpu.record_process_finish_time(time)
        cpu.record_gantt(PS.name)

    ''' Analysis '''
    FCFS.calculate_results()
    SJF.calculate_results()
    SRTF.calculate_results()
    RR.calculate_results()
    PS.calculate_results()

    ''' Compile the results to pass to the App '''
    # TODO Fix the way results are saved and stored - pretty clunky
    max_simulation_time = simulation.determine_simulation_time()
    print 'FFF', max_simulation_time
    for algorithm in ALGORITHMS:
        # Trimming the GANTT chart "None" tail
        parsed_gantt = GANTT[algorithm][0:max_simulation_time]

        RESULTS[algorithm].update({
            'GANTT': parsed_gantt,
        })

    return RESULTS


if __name__ == '__main__':
    run_simulation()

    pprint.pprint(RESULTS)
