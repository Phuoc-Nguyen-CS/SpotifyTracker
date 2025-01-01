import subprocess
import time

def run_script():
    try:
        subprocess.run(["python", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occured: {e}")
    
while True:
    run_script()
    time.sleep(60)
