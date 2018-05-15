import json
from subprocess import Popen, PIPE
import io

def judge_handle(event, context):
    print('=================!!!!!=====')
    print(type(event))
    print(event)
    print('=================?????=====')
    
    
    proc = Popen(['python', 'run.py'], stdin=PIPE, stdout=PIPE)
    try:
        outs, errs = proc.communicate(
            input=json.dumps(event).encode('utf8'),
            timeout=int(context.get_remaining_time_in_millis() / 1000)
        )
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        
    print(outs, errs)
    
    return json.loads(outs.decode('utf8'))
    