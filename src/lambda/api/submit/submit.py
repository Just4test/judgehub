'''

'''
import sys
if not ('packages' in sys.path):
    sys.path.insert(0, 'packages')

import boto3
import botocore
import json
import yaml
import os

from pathlib import Path


# __import__('patch').load('.resource_map.yaml')
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
JUDGE_LAMBDA = {
	'python3': os.environ['JUDGE_PYTHON3'],
	'nodejs': os.environ['JUDGE_NODEJS'],
}

def respond(err, res=None):
	if not isinstance(res, str):
		res = json.dumps(res)
	return {
		'statusCode': '400' if err else '200',
		'body': json.dumps({'error':str(err)}) if err else res,
		'headers': {
			'Content-Type': 'application/json',
		},
	}

def create_data(problem):
	download(problem)
	
	with open(f'/tmp/problems/{problem}/metadata.yaml') as f:
		metadata = yaml.load(f)
	with open(f'/tmp/problems/{problem}/testcase.yaml') as f:
		testcase = yaml.load(f)
		
	judge_data = {
		'params': metadata['params'],
		'method': metadata['method'],
		'testcase': [ case['input'] for case in testcase ]
	}
	return judge_data, testcase
	
	
def download(problem):
	path = Path(f'/tmp/problems/{problem}')
	if os.path.isdir(path):
		print(f'Path {path} already created.')
	else:
		path.mkdir(parents=True)
	
	
	def down(path, to):
		try:
			print(S3_BUCKET_NAME, path, to)
			s3.download_file(S3_BUCKET_NAME, path, to)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print(f'Object "{path}" does not exist on s3.')
			else:
				raise
	down(f'data/problems/{problem}/metadata.yaml', f'/tmp/problems/{problem}/metadata.yaml')
	down(f'data/problems/{problem}/testcase.yaml', f'/tmp/problems/{problem}/testcase.yaml')


def submit_handle(event, context):
	def get_header(key):
		if 'headers' not in event:
			return None
		key = key.lower()
		for k, v in event['headers'].items():
			if k.lower() == key:
				return v
		return None
	content_type = get_header('Content-Type')
	if content_type is None or 'application/json' not in content_type:
		return respond(ValueError('Must provide json as body.'))

	'''
	# metadata
	{
		runtime: python3
		problem_id: 1
		code: //todo
	}
	# testcase
	[
		{
			input: [1, 2]
			expected: 3
		}
	]
	'''
	try:
		body = yaml.safe_load(event['body'])
	except BaseException as e:
		return respond(ValueError('Body must be json string'))
	if not isinstance(body, dict):
		return respond(ValueError('Body must be json dict'))
	code = body['code']
	problem = body['problem_id']
	runtime = body['runtime']
	if not isinstance(code, str) or not isinstance(problem, str) or not isinstance(runtime, str):
		return respond(ValueError('Body must contain runtime/problem_id/code'))
		

	judge_data, testcase = create_data(problem)
	judge_data['code'] = code
	judge_data['timeout'] = 3000
	payload = json.dumps(judge_data).encode('utf-8')
	judge_lambda_name = JUDGE_LAMBDA[runtime]
	print(f'======= Call Judge Lambda {judge_lambda_name} ========\n{payload}')
	temp = lambda_client.invoke(
		FunctionName=judge_lambda_name,
		Payload=payload
	)

	result = json.loads(temp['Payload'].read().decode('utf8'))
	print(f'======= Judge Lambda Return ========\n{result}\n====================================')

	'''
	# Normal exit
	{
		runtime: 0.001
		results: [
			{
				output: 1
				stdout: xxxxx
			}
		]
	}
	# Runtime error
	{
		error: Exception xxxx
		case_p: 0 # -1 to length(testcase). -1 means error occered in init code.
		stdout: xxxxxxx
	}
	'''
	
	if 'error' in result:
		if result['error'] == '__TLE__':
			ret = {
				'status': 'TLE'
			}
		else:
			ret = {
				'status': 'RE',
				'error': result['error'],
				'stdout': result['stdout'],
				'stderr': result.get('stderr', None),
			}
			case_p = result['case_p']
			if case_p >= 0:
				ret['input'] = testcase[case_p]['input']
				ret['expected'] = testcase[case_p]['expected']
	else:
		r = result['results']
		for i in range(len(testcase)):
			expected = testcase[i]['expected']
			output = r[i]['output']
			if expected != output:
				ret = {
					'status': 'WA',
					'input': testcase[i]['input'],
					'output': output,
					'expected': expected,
					'stdout': r[i]['stdout'],
				}
				break
		else:
			ret = {
				'status': 'AC',
				'run_duration': int(result['run_duration']),
			}
		

	return respond(None, ret)


#result = lambda_client.invoke(
#	FunctionName='OnlineJudge/OJJudgePython3',
#)
#
#print(result)
