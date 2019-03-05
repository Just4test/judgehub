import sys
import imp
import json
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

try:
    run()
except BaseException as e:
    stdout.seek(stdout_p)
    ret = {
        'error': repr(e),
        'case_p': case_p,
        'stdout': stdout.read()
    }
    if case_p >= 0:
        ret['LastInput'] = testcase[case_p]
else:
    ret = {
        'results': results
    }

stdout.close()
sys.stdout = _stdout
print(json.dumps(ret))
    