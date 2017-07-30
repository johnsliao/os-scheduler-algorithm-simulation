import random
import copy
from collections import deque

SIMULATION_SPEED = 1
NUMBER_OF_PROCESSES = 10
GANTT = {}
TIME_QUANTUM = 3


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
    def __init__(self, pid):
        self.pid = pid
        self.arrival_time = 0
        self.burst_time = 0
        self.remaining_burst_time = 0
        self.priority = 0
        self.start = 0

        self.setup()

    def setup(self):
        self.arrival_time = int(random.uniform(0, 10))
        self.priority = int(random.uniform(1, 10))
        self.burst_time = int(random.uniform(1, 10))
        self.remaining_burst_time = self.burst_time


class Simulation():
    def __init__(self):
        self.process_pool = set()

        self.setup()

    def setup(self):
        # Generate Process instances and add them to the pool
        # pid is assigned sequentially
        for pid in range(1, NUMBER_OF_PROCESSES):
            self.process_pool.add(Process(pid))

    def pprint_process_pool(self):
        processes = sorted(self.process_pool)
        for process in processes:
            print 'pid %s: Arrival time: %s, Burst Time: %s, Prio: %s, remainingburst: %s' % (
                process.pid, process.arrival_time, process.burst_time, process.priority, process.remaining_burst_time)


class Algorithm():
    def __init__(self):
        pass

    def check_process_arrivals(self, time):
        """ Add process to deque the process if arrival time matches current time """

        for process in self.simulation.process_pool:
            if time == process.arrival_time:
                self.deque.append(process)


class FirstComeFirstServe(Algorithm):
    def __init__(self, simulation):
        Algorithm.__init__(self)

        self.name = 'First Come First Serve'
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

        self.name = 'Shortest Job First'
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

        self.name = 'Shortest Remaining Time First'
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

        self.name = 'RoundRobin'
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

        self.name = 'Priority Scheduling'
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


if __name__ == '__main__':
    simulation = Simulation()
    simulation.pprint_process_pool()
    cpu = CPU()

    ''' First Come First Serve '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    FCFS = FirstComeFirstServe(simulation)

    for time in range(0, 100):
        FCFS.check_process_arrivals(time)

        #  Non-premptive algorithm
        if cpu.is_process_complete():
            cpu.ingest_process(FCFS.get_first_process())

        cpu.decrement_process()
        cpu.record_gantt(FCFS.name)

    ''' Shortest Job First '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    SJF = ShortestJobFirst(simulation)

    for time in range(0, 100):
        SJF.check_process_arrivals(time)
        SJF.remove_expired_jobs_from_pool()

        #  Non-premptive algorithm
        if cpu.is_process_complete():
            cpu.ingest_process(SJF.get_shortest_job_from_pool())

        cpu.decrement_process()
        cpu.record_gantt(SJF.name)

    ''' Shortest Remaining Time First '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    SRTF = ShortestRemainingTimeFirst(simulation)

    for time in range(0, 100):
        SRTF.check_process_arrivals(time)
        SRTF.remove_expired_jobs_from_pool()

        cpu.ingest_process(SRTF.get_shortest_remaining_time_from_pool())
        cpu.decrement_process()
        cpu.record_gantt(SRTF.name)

    ''' Round Robin '''
    cpu.reset()  # Reset cpu for next algorithm simulation
    RR = RoundRobin(simulation)

    current_time_quantum = 0
    current_process = None
    for time in range(0, 100):
        RR.check_process_arrivals(time)

        if current_process is None or current_time_quantum >= TIME_QUANTUM or current_process.remaining_burst_time == 0:
            current_process = RR.get_next_process()
            current_time_quantum = 0
        else:
            current_process = RR.get_current_process()

        cpu.ingest_process(current_process)

        cpu.decrement_process()
        cpu.record_gantt(RR.name)

        current_time_quantum += 1

    ''' Priority Scheduling '''

    cpu.reset()  # Reset cpu for next algorithm simulation
    PS = PriorityScheduling(simulation)

    for time in range(0, 100):
        PS.check_process_arrivals(time)
        PS.remove_expired_jobs_from_pool()

        cpu.ingest_process(PS.get_lowest_priority_from_pool())
        cpu.decrement_process()
        cpu.record_gantt(PS.name)

    print GANTT
