import time
import ssmenv
import os


from jwt import (
  JWT,
  jwk_from_dict,
  jwk_from_pem,
)



private_key = jwk_from_pem(os.environ['GITHUB_APP_PRIVATE_PEM'].encode())

timestamp = int(time.time())
payload = {
  'iss': os.environ['GITHUB_APP_ID'],
  'iat': timestamp,
  'exp': timestamp + 60,
}
jwt = JWT()
compact_jws = jwt.encode(payload, private_key, 'RS256')
print(compact_jws)