import boto3
#cloudformation = boto3.resource('cloudformation')

resource_map = None
def load(path):
	global resource_map
	with open(path, 'r') as f:
		if path.endswith('.yaml') or path.endswith('.yml'):
			resource_map = __import__('yaml').load(f)
		else:
			resource_map = __import__('json').load(f)
	
def lambda_invoke(function):
	def wrap_function(*args, **kwargs):
		if resource_map is None:
			raise RuntimeError('You must call patch.load() to init patch package.')
		if 'FunctionName' in kwargs and '/' in kwargs['FunctionName']:
			stack_name, logical_id = kwargs['FunctionName'].split('/', 1)
			if '/' in logical_id:
				raise ValueError('There are more than one "/" in FunctionName')
			logical_id = logical_id.split(':')[0]
#			stack_resource = cloudformation.StackResource(stack_name, logical_id)
#			kwargs['FunctionName'] = stack_resource.physical_resource_id
			if stack_name not in resource_map:
				raise ValueError('There are no stack named "{}" in resource map file.'.format(stack_name))
			if logical_id not in resource_map[stack_name]:
				raise ValueError('There are no resource with logical id "{}" in stack "{}"'.format(logical_id, stack_name))
			kwargs['FunctionName'] = resource_map[stack_name][logical_id]
		return function(*args, **kwargs)
	return wrap_function
	
client_patchmap = {
	'lambda':{
		'invoke':lambda_invoke
	}
}

def wrap_client(function):
	def wrap_function(*args, **kwargs):
		client = function(*args, **kwargs)
		service_name = kwargs.get('service_name') or args[0]
		if service_name in client_patchmap:
			for method_name, wrap in client_patchmap[service_name].items():
				new_method = wrap(getattr(client, method_name))
				setattr(client, method_name, new_method)
		return client
	return wrap_function
				
boto3.client = wrap_client(boto3.client)
			
#cloudformation = boto3.resource('cloudformation')
#lambda_client = boto3.client('lambda')
#print(lambda_client)
#result = lambda_client.invoke(
#	FunctionName='OnlineJudge/OJSubmit',
#)

#print(result)