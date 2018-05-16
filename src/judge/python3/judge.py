import json
from subprocess import Popen, PIPE, TimeoutExpired
import io
from time import time, sleep

#Create subprocess here, so subprocess can run init code first. 
def judge_handle(event, context):
    print('=================!!!!!=====')
    print(type(event))
    print(event)
    print('=================Run subprocess=====')
    proc = Popen(['python', 'run.py'], stdin=PIPE, stdout=PIPE)
    sleep(0.09) #When run in 2048mb lambda, 0.07 is enough to finish init code.

    t = -time()
    try:
        outs, errs = proc.communicate(
            input=json.dumps(event).encode('utf8'),
            timeout=int(context.get_remaining_time_in_millis() / 1000)
        )
        t += time()
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    outs = outs.decode('utf8')
    result = json.loads(outs)
    if t > 0:
        result['runtime'] = t
    print('=================Subprocess end=====')
    print('OUT>>>>>>>>\n{}\nERROR>>>>>>>>\n{}'.format(result, errs))

    proc = Popen(['python', 'run.py'], stdin=PIPE, stdout=PIPE)
    return result
    