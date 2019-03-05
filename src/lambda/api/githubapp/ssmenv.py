import os
import boto3

client = boto3.client('ssm')

for key, value in os.environ.items():
  if value.find('ssm:') != 0:
    continue
  
  try:
    response = client.get_parameter(Name=value[4:], WithDecryption=True)
    os.environ[key] = response['Parameter']['Value']
#    print(key, os.environ[key])
  except Exception as e:
    print(e, key, value)
    