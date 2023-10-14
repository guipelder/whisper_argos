"""
this file is for testing the log.txt functionality
after running you need to open the log.txt and 
add some lines to it 
the watch the terminal for seeing the log change
"""

import asyncio

def read_log():

        with open("log.txt", "r") as f:
            SMRF1 = f.readlines()
        return SMRF1
    
initial = read_log()

async def on_log_change():

        while True:
            current = read_log()
            global initial
            if initial != current:
                for line in current:
                    if line not in initial:
                        print(f"change in log->  {line}")
                        #log_sender(line)
                        initial = current
            await asyncio.sleep(1)

def stop():                        
    task.cancel()

try:
    loop = asyncio.get_event_loop()
except RuntimeError as e:
    if str(e).startswith('There is no current event loop'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        raise

task = loop.create_task(on_log_change())
    
   
try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass  
