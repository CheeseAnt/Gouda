import subprocess
import time

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode('utf-8')
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name)

while True:
    if not process_exists("notepad.exe"):
        f = open("compliance.txt", "w")
        f.write("You are not intel compliant.")
        f.close()

        print("Incompliance detected")
        
        subprocess.call("notepad compliance.txt")
    else:
        print("User is compliant.")

    time.sleep(5)

