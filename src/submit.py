'''

'''
__import__('patch').load('.resource_map.yaml')
import boto3
import json

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

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


def submit_handle(event, context):
	if 'headers' not in event or 'Content-Type' not in event['headers'] or 'application/json' not in event['headers']['Content-Type']:
		return respond(ValueError('Must provide json as body.'))
		
	'''
	{
		lang: python3
		problem_id: 1
		code: //todo
	}
	'''
		
	body = json.loads(event['body'])
	if not isinstance(body, dict) or 'lang' not in body or 'problem_id' not in body or 'code' not in body:
		return respond(ValueError('Body must contain lang/problem_id/code'))
	
	print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	result = lambda_client.invoke(
		FunctionName='OnlineJudge/OJJudgePython3',
#		InvocationType='Event'
	)
	
	print(result)
	payload = result['Payload']
	temp = payload.read()
	print('~~~~~~', isinstance(temp, bytes), type(temp), temp)
	if isinstance(temp, bytes):
		print('fuck!')
		temp = temp.decode('utf8')
	print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print(temp)
	
	return respond(None, temp)
		
		
result = lambda_client.invoke(
	FunctionName='OnlineJudge/OJJudgePython3',
)

print(result)
	