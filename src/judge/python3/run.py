import sys
import imp
import json
from time import time
import io

data = json.loads(input())
testcase = data['testcase']
code = data['code']
results = []
case_p = -1

stdout = io.StringIO()
_stdout = sys.stdout
sys.stdout = stdout
stdout_p = 0

def run():
    global stdout_p, case_p
    UserModule = imp.new_module('UserModule')
    exec(code, UserModule.__dict__)
    
#	if not hasattr(UserModule, 'Solution'):
#		raise Exception('There are no "Solution" class in your code.')
    s = UserModule.Solution()
#	if not hasattr(s, data['method']):
#		raise Exception('There are no "{}" method in class "Solution"'.format(data['method']))
    method = getattr(s, data['method'])
    for case in testcase:
        case_p += 1
        stdout_p = stdout.tell()
        output = method(*case)
        stdout.seek(stdout_p)
        results.append({
            'output': output,
            'stdout': stdout.read()
        })
        
run()
start_time = time()
try:
    run()
except BaseException as e:
    stdout.close()
    sys.stdout = _stdout
    if case_p >= 0:
        ret['LastInput'] = case[case_p]
    
    stdout.seek(stdout_p)
    ret = {
        'error': repr(e),
        'case_p': case_p,
        'stdout': stdout.read()
    }
else:
    end_time = time()
    stdout.close()
    sys.stdout = _stdout

    ret = {
        'runtime': end_time - start_time,
        'results': results
    }

print(json.dumps(ret))
    