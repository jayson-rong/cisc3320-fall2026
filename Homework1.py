import os


# Print PID and PPID

def get_PIDandPPID():

    PID = os.getpid()
    PPID = os.getppid()

    print(f"Process ID: {PID}")
    print(f"Parent Process ID: {PPID}")

# Print key and value

def get_environVar():

    envir_var = os.environ.items()

    # Loop through each key that matches the value

    for key, value in envir_var:
        print(f"{key} = {value}")

# Print file descriptor

def get_fileDescript():
    fileDes = os.listdir('/proc/self/fd')

    # Loop through the file to get a file descriptor

    for file in fileDes:
        print(file)


if __name__ == "__main__":

    # Call function to get PID and PPID
    get_PIDandPPID()

    # Call function to get environment variable
    get_environVar()

    #Call function to get file descriptor
    get_fileDescript()


