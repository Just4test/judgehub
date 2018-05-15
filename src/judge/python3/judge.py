import json
from subprocess import Popen, PIPE
import io

def judge_handle(event, context):
    print('=================!!!!!=====')
    print(type(event))
    print(event)
    print('=================Run subprocess=====')
    
    
    proc = Popen(['python', 'run.py'], stdin=PIPE, stdout=PIPE)
    try:
        outs, errs = proc.communicate(
            input=json.dumps(event).encode('utf8'),
            timeout=int(context.get_remaining_time_in_millis() / 1000)
        )
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        
    outs = outs.decode('utf8')
    print('=================Subprocess end=====')
    print('OUT>>>>>>>>\n{}\nERROR>>>>>>>>\n{}'.format(outs, errs))
    
    return json.loads(outs)
    