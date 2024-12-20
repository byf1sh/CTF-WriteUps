from flask import request, abort
import functools, requests
from urllib.parse import urlparse

RESTRICTED_URLS = ['localhost', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def is_safe_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if not hostname:
        return False
    for restricted_url in RESTRICTED_URLS:
        if restricted_url in hostname:
            return False
    return True

def is_from_localhost(func):
    @functools.wraps(func)
    def check_ip(*args, **kwargs):
        if request.remote_addr != '127.0.0.1':
            print(request.remote_addr)
            print('kena filter localhost')
            return abort(403)
        return func(*args, **kwargs)
    return check_ip

def proxy_req(url):
    method = request.method
    headers =  {
        key: value for key, value in request.headers if key.lower() in ['x-csrf-token', 'cookie', 'referer']
    }
    data = request.get_data()
    print(f'method {method}')
    print(f'url {url}')
    print(f'headers dari url {headers}')
    print(f'data dari url {data}')
    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        verify=False
    )
    print(f'Status Code: {response.status_code}')
    print(f'Headers: {response.headers}')
    print(f'Body: {response.text}')


    if not is_safe_url(url) or not is_safe_url(response.url):
        print('kena proxy')
        return abort(403)
    
    return response, headers