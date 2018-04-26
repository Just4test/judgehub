import boto3
import json



client = boto3.client('cloudformation')
output='../src/.resource_map.yaml'

if output.endswith('.yaml') or output.endswith('.yml'):
	try:
		import yaml
	except:
		print('Need PyYaml package to save yaml file.')
		exit(1)

response = client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])

if response['ResponseMetadata']['HTTPStatusCode'] != 200:
	print('List stacks failed. return:\n{}'.format(response))
	exit(1)

data = {}

def list_resources(stack_name, next_token=None, result=None):
	result = result or {}
	if next_token:
		response = client.list_stack_resources(StackName=stack_name, NextToken=next_token)
	else:
		response = client.list_stack_resources(StackName=stack_name)
	if response['ResponseMetadata']['HTTPStatusCode'] != 200:
		print('List resource in {} failed. return:\n{}'.format(stack_name, response))
		exit(1)
	for resource in response['StackResourceSummaries']:
		result[resource['LogicalResourceId']] = resource['PhysicalResourceId']
	if 'NextToken' in response:
		list_resources(stack_name, response['NextToken'], result)
	return result

for s in response['StackSummaries']:
	name = s['StackName']
	print(name)
	data[name] = list_resources(name)

with open(output, 'w') as outfile:
	if output.endswith('.yaml') or output.endswith('.yml'):
		yaml.dump(data, outfile, default_flow_style=False)
	else:
		json.dump(data, outfile)
	