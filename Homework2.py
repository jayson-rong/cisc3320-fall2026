import os
import signal

class Job:
    def __init__(self, pid, command, background):
        self.pid = pid
        self.command = command
        self.background = background
        self.status = "Running"

class Shell:

    def __init__(self):
        self.jobs = {}
        self.next_job_id = 1

    def parse(self, command):
        
        command = command.strip()

        if len(command) == 0:
            return [], False

        background = False

        if command.endswith("&"):
            background = True
            command = command[:-1].strip()

        command_Line = command.split()

        return command_Line, background

    # Run backgrgound jobs
    def run_background(self, command):
        
        command_string = " ".join(command)

        # Child process
        pid = os.fork()

        if pid == 0:
            
            try:
                os.execvp(command[0], command)
            
            except Exception:
                print(f"{command[0]}: command not found")
                os._exit(1)
        else:

            # Parent process
            job = Job(pid, command_string, True)
            self.jobs[self.next_job_id] = job
            
            print("[" + str(self.next_job_id) + "] " + str(pid))
            self.next_job_id += 1

    # Show all jobs
    def show_jobs(self):

        for job_number in self.jobs:

            job = self.jobs[job_number]
            
            print(f"[{job_number}] {job.status} {job.command}")

    # Reape process 
    def reap_zombies(self):

        for job_id in self.jobs:

            if self.jobs[job_id].status == "Running":
                
                # Reap child process
                pid, status = os.waitpid(self.jobs[job_id].pid, os.WNOHANG)
            
                # Child process has finished executing
                if pid != 0:
                    self.jobs[job_id].status = "Done"
    
    # Run foreground jobs
    def run_foreground(self, job_num):

        if job_num not in self.jobs:
            print("myshell>: no such job")
            return
        
        job = self.jobs[job_num]
        
        if job.status == "Running":
            
            print(job.command)
            os.waitpid(job.pid,0)
            job.status = "Done"

    def stop_job(self, job_num):
        
        if job_num not in self.jobs:
            print("myshell>: no such job")
            return

        job = self.jobs[job_num]
        os.kill(job.pid, signal.SIGINT)
        job.status = "STOPPED"

    # Kill job
    def kill_job(self, command):

        splitting_str = command.split()
        commandLine = splitting_str[-1] # Store and remove the job number at index -1 -> job_num
        
        job_num = int(commandLine[1:])

        if job_num not in self.jobs:
            print("myshell>: no such job")
            return
        
        job = self.jobs[job_num]
        
        if job.status == "Running":
                        
            os.kill(job.pid, signal.SIGTERM)
            os.waitpid(job.pid,0)
            job.status = "Terminated"

    # Run the shell
    def start(self):
    
        running = True
    
        while running:
                
            self.reap_zombies()
            command = input("myshell> ")
            running = self.handle_command(command)
    
    # Handle different commands
    def handle_command(self, command):
            
            string_split, background = self.parse(command)
    
            # Return to myshell
            if len(string_split) == 0:
                return True

            cmd = string_split[0]
    
            if cmd == "jobs":
                self.show_jobs()
    
            elif cmd == "fg":
                string_WD = string_split[1]
                
                if string_WD.startswith("%"):
                    job_num = int(string_WD[1:])
                
                else:
                    job_num = int(string_WD)
                self.run_foreground(job_num)
    
            elif cmd == "kill":
                self.kill_job(command)
    
            else:
                if background:
                    self.run_background(string_split)
    
                # Other commands
                else:
                    
                    pid = os.fork()
                    
                    if pid == 0:
                        
                        try:
                            os.execvp(string_split[0], string_split)
                        except Exception:
                            print(f"myshell>: " + string_split[0] + ": command not found")
                            os._exit(1)
                    
                    else:
                        os.waitpid(pid, 0)
            return True

if __name__ == "__main__":
    shell = Shell()
    shell.start()