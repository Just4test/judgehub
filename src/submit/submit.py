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
	
	with open('/tmp/problems/{}/metadata.yaml'.format(problem)) as f:
		metadata = yaml.load(f)
	with open('/tmp/problems/{}/testcase.yaml'.format(problem)) as f:
		testcase = yaml.load(f)
		
	judge_data = {
		'params': metadata['params'],
		'method': metadata['method'],
		'testcase': [ case['input'] for case in testcase ]
	}
	return judge_data, testcase
	
	
def download(problem):
	path = Path('/tmp/problems/{}'.format(problem))
	if os.path.isdir(path):
		print('Path {} already created.'.format(path))
	else:
		path.mkdir(parents=True)
	
	
	def down(path, to):
		try:
			print(S3_BUCKET_NAME, path, to)
			s3.download_file(S3_BUCKET_NAME, path, to)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print('Object "{}" does not exist on s3.'.format(path))
			else:
				raise
	down('data/problems/{}/metadata.yaml'.format(problem), '/tmp/problems/{}/metadata.yaml'.format(problem))
	down('data/problems/{}/testcase.yaml'.format(problem), '/tmp/problems/{}/testcase.yaml'.format(problem))


def submit_handle(event, context):
	if 'headers' not in event or 'Content-Type' not in event['headers'] or 'application/json' not in event['headers']['Content-Type']:
		return respond(ValueError('Must provide json as body.'))

	'''
	# metadata
	{
		lang: python3
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
	lang = body['lang']
	if not isinstance(code, str) or not isinstance(problem, str) or not isinstance(lang, str):
		return respond(ValueError('Body must contain lang/problem_id/code'))
		

	judge_data, testcase = create_data(problem)
	judge_data['code'] = code
	judge_data['timeout'] = 3000
	payload = json.dumps(judge_data).encode('utf-8')
	judge_lambda_name = JUDGE_LAMBDA[lang]
	print('======= Call Judge Lambda {} ========\n{}'.format(judge_lambda_name, payload))
	temp = lambda_client.invoke(
		FunctionName=judge_lambda_name,
		Payload=payload
	)

	result = json.loads(temp['Payload'].read().decode('utf8'))
	print('======= Judge Lambda Return ========\n{}\n===================================='.format(result))

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
