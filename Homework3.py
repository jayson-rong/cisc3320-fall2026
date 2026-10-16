from pathlib import Path
import heapq

class simProcess:
     def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority

        self.start_time = None
        self.completion_time = 0
        self.turnAround_time = 0
        self.waiting_time = 0
        self.response_time = 0
        self.inQueue = False

class CPUScheduling:
    def __init__(self):
        self.readyQ = []
        self.completedQ = []
        self.processList = []
        self.currentTime = 0
                    
    def calculateCompletionTime(self, p):

        for process in p:
            if self.currentTime < process.arrival_time:
                self.currentTime = process.arrival_time

            process.start_time = self.currentTime
            process.completion_time = (self.currentTime + process.burst_time)
            self.currentTime = process.completion_time

    def calculateTurnAroundTime(self, p):
        for process in p:
            process.turnAround_time = (process.completion_time - process.arrival_time)

    def calculateWaitingTime(self, p):
        for process in p:
            process.waiting_time = (process.turnAround_time - process.burst_time)

    def calculateResponseTime(self, p):
        for process in p:
            process.response_time = (process.start_time - process.arrival_time)

    def calculateAverageTAT(self, p):

        total_TAT = 0

        for process in p:
            total_TAT = total_TAT + process.turnAround_time

        avg = total_TAT / len(p)
        print(f"\nAverage Turnaround Time: {avg} units of time")

    def calculateAverageWT(self, p):
        
        total_WT = 0

        for process in p:
            total_WT = total_WT + process.waiting_time

        avg = total_WT / len(p)
        print(f"Average Waiting Time: {avg} units of time")
    
    def calculateAverageRT(self, p):
        total_RT = 0
        
        for process in p:
            total_RT = total_RT + process.response_time
        
        avg = total_RT / len(p)
        print(f"Average Response Time: {avg} units of time")

    def FCFS(self):
        self.read_file()

        for process in self.processList:
            self.readyQ = self.readyQ + [process]

        while len(self.readyQ) > 0:
            process = self.readyQ.pop(0)

            if self.currentTime < process.arrival_time:
                self.currentTime = process.arrival_time

            process.start_time = self.currentTime
            process.completion_time = self.currentTime + process.burst_time

            self.currentTime = process.completion_time

            self.completedQ = self.completedQ + [process]

    
        self.calculateTurnAroundTime(self.completedQ)
        self.calculateWaitingTime(self.completedQ)
        self.calculateResponseTime(self.completedQ)

    
        self.displayTable(self.completedQ)
        self.calculateAverageTAT(self.completedQ)
        self.calculateAverageWT(self.completedQ)
        self.calculateAverageRT(self.completedQ)

    def addNewArrivals(self, time_now):
        for process in self.processList:
            is_new_arrival = (process.arrival_time <= time_now and process.remaining_time > 0 and not process.inQueue)
        
            if is_new_arrival:
                self.readyQ = self.readyQ + [process]
                process.inQueue = True
                            
    def RR(self, quantum):

        self.read_file()

        time_now = 0

        self.addNewArrivals(time_now)

        # Check for more processes arriving
        while len(self.readyQ) > 0 or len(self.completedQ) < len(self.processList):

            if len(self.readyQ) == 0:
                time_now = time_now + 1
                self.currentTime = time_now

                self.addNewArrivals(time_now)
                continue

            processNow = self.readyQ.pop(0)

            if processNow.start_time == None:
                processNow.start_time = time_now

            if processNow.remaining_time < quantum:
                timeRunningOnCPU = processNow.remaining_time
            else:
                timeRunningOnCPU = quantum

            processNow.remaining_time = processNow.remaining_time - timeRunningOnCPU

            time_now = time_now + timeRunningOnCPU
            self.currentTime = time_now

            self.addNewArrivals(time_now)

            if processNow.remaining_time == 0:
                processNow.completion_time = time_now
                self.completedQ = self.completedQ + [processNow]
                processNow.inQueue = False
            else:
                self.readyQ = self.readyQ + [processNow]
                processNow.inQueue = True

        self.calculateTurnAroundTime(self.completedQ)
        self.calculateWaitingTime(self.completedQ)
        self.calculateResponseTime(self.completedQ)

        self.completedQ.sort(key=lambda p: str(p.pid))

        self.displayTable(self.completedQ)
        self.calculateAverageTAT(self.completedQ)
        self.calculateAverageWT(self.completedQ)
        self.calculateAverageRT(self.completedQ)

    def priority_schedule(self):
        self.read_file()

        for i in range(len(self.processList)):
            process = self.processList[i]

            heapq.heappush(self.readyQ,(process.priority,process.arrival_time, process.pid, i, process))

        while self.readyQ:
            priority, arrival_time, pid, i , process = heapq.heappop(self.readyQ)

            if self.currentTime < process.arrival_time:
                self.currentTime = process.arrival_time

            process.start_time = self.currentTime
            process.completion_time = self.currentTime + process.burst_time

            self.currentTime = process.completion_time
            self.completedQ.append(process)

        self.calculateTurnAroundTime(self.completedQ)
        self.calculateWaitingTime(self.completedQ)
        self.calculateResponseTime(self.completedQ)

        self.displayTable(self.completedQ)
        self.calculateAverageTAT(self.completedQ)
        self.calculateAverageWT(self.completedQ)
        self.calculateAverageRT(self.completedQ)
    
    def SJF(self):
        self.read_file()

        while len(self.completedQ) < len(self.processList):

            for process in self.processList:
                if process.arrival_time <= self.currentTime and process not in self.readyQ and process not in self.completedQ:
                    self.readyQ = self.readyQ + [process]

            if len(self.readyQ) == 0:
                for process in self.processList:
                    if process not in self.completedQ:
                        self.currentTime = process.arrival_time
                        break
                continue

            # Swap the burst time
            for i in range(len(self.readyQ) - 1):
                for j in range(len(self.readyQ) - 1 - i):
                    if self.readyQ[j].burst_time > self.readyQ[j + 1].burst_time:
                        temp = self.readyQ[j]
                        self.readyQ[j] = self.readyQ[j + 1]
                        self.readyQ[j + 1] = temp

            process = self.readyQ.pop(0)
            process.start_time = self.currentTime
            process.completion_time = self.currentTime + process.burst_time
            self.currentTime = process.completion_time
            self.completedQ = self.completedQ + [process]

        self.calculateTurnAroundTime(self.completedQ)
        self.calculateWaitingTime(self.completedQ)
        self.calculateResponseTime(self.completedQ)

        self.displayTable(self.completedQ)
        self.calculateAverageTAT(self.completedQ)
        self.calculateAverageWT(self.completedQ)
        self.calculateAverageRT(self.completedQ)

    def MLFQ_schedule(self, quantum0, quantum1, quantum2):
        self.read_file()
        Q0 = []
        Q1 = []
        Q2 = []

        first_Quantum = quantum0
        second_Quantum = quantum1
        third_Quantum = quantum2

    # Add all the processes to Q0
        for i in range(len(self.processList)):
            Q0 = Q0 + [self.processList[i]]

    # Run processes in Q0
        for i in range(len(Q0)):
            process = Q0[i]

            if process.start_time is None:
                process.start_time = self.currentTime

        # Track of CPU run time
            runTime = min(process.remaining_time, first_Quantum)

            self.currentTime = self.currentTime + runTime
            process.remaining_time = process.remaining_time - runTime

            if process.remaining_time == 0:
                process.completion_time = self.currentTime
                self.completedQ = self.completedQ + [process]
            else:
                Q1 = Q1 + [process]

    # Run processes in Q1
        for i in range(len(Q1)):
            process = Q1[i]

            runTime = min(process.remaining_time, second_Quantum)

            self.currentTime = self.currentTime + runTime
            process.remaining_time = process.remaining_time - runTime

            if process.remaining_time == 0:
                process.completion_time = self.currentTime
                self.completedQ = self.completedQ + [process]
            else:
                Q2 = Q2 + [process]

    # Run processes in Q2
        for i in range(len(Q2)):
            process = Q2[i]

            runTime = min(process.remaining_time, third_Quantum)

            self.currentTime = self.currentTime + runTime
            process.remaining_time = process.remaining_time - runTime

            if process.remaining_time == 0:
                process.completion_time = self.currentTime
                self.completedQ = self.completedQ + [process]

    # Calculate metrics
        self.calculateTurnAroundTime(self.completedQ)
        self.calculateWaitingTime(self.completedQ)
        self.calculateResponseTime(self.completedQ)

        self.displayTable(self.completedQ)
        self.calculateAverageTAT(self.completedQ)
        self.calculateAverageWT(self.completedQ)
        self.calculateAverageRT(self.completedQ)

    def read_file(self):
            myFile = Path("data.txt")
    
            with open(myFile, "r") as scan:
                for line in scan:
                    data = line.strip().split(",")
                
                    pid = str(data[0])
                    
                    arrivalTime = int(data[1])
                    
                    # For SJF
                    burstTime = int(data[2])
                    
                    prior = int(data[3])

                    # For MLFQ, SJF, Priority --> pid, arrival, burst, prior
                    self.processList = self.processList + [simProcess(pid, arrivalTime, burstTime, prior)]
                    
                    # For RR --> pid, arrival, burst
                    # self.processList = self.processList + [simProcess(pid, arrivalTime, burstTime)]
    
    def displayTable(self, p):
            label = "{:<5} | {:<2} | {:<5} | {:<8} | {:<5} | {:<10} | {:<10} | {:<7} | {:<8}".format(
            "PID",
            "Arrival",
            "Burst", 
            "Priority",
            "Start",
            "Completion",
            "Turnaround",
            "Waiting",
            "Response"
            )   
            
            print("\n                         CPU Scheduling Table")
            print("-" * 95)
            print(label)
            print("-" * 95)
    
            for process in p:
                print("{:<5} | {:<7} | {:<5} | {:<8} | {:<5} | {:<10} | {:<10} | {:<7} | {:<8}".format(process.pid, process.arrival_time, process.burst_time, process.priority, process.start_time, process.completion_time, process.turnAround_time, process.waiting_time, process.response_time))
    
            print("-" * 95)

    def compare(self):
        print("{:<20} {:<20} {:<20} {:<20}".format(
            "Algorithm",
            "Avg Waiting Time",
            "Avg Turnaround Time",
            "Avg Response Time"
        ))

        print("-" * 80)

        results = [
        ["FCFS", 5.5, 9.0, 5.5],
            ["SJF", 3.0, 6.5, 3.0],
            ["Priority", 7.25, 10.75, 7.25],
            ["Round Robin", 6.25, 9.75, 4.5],
            ["MLFQ", 6.25, 9.5, 4.5]
        ]
        for result in results:
            print("{:<20} {:<20.2f} {:<20.2f} {:<20.2f}".format(result[0],result[1],result[2],result[3]))

if __name__ == "__main__":
    
    # fcfs_schedule = CPUScheduling()
    # fcfs_schedule.FCFS()

    # prior_schedule = CPUScheduling()
    # prior_schedule.priority_schedule()
      
    # MLFQ = CPUScheduling()
    # MLFQ.MLFQ_schedule(4,8,16)

    #  RR_schedule = CPUScheduling()
    #  RR_schedule.RR(4)

    # SJF_schedule = CPUScheduling()
    # SJF_schedule.SJF()
    
    compare_result = CPUScheduling()
    compare_result.compare()