# Proxy usage with Python

## [aiosocks](https://pypi.org/project/aiosocks/)

```python
import asyncio
import aiosocks

async def proxy_example(proxy: str, use_ssl:  bool = False):
    '''Proxy can be in IP:PORT format or USER:PASS@IP:PORT format'''

    auth = proxy.split('@')[0].split(':') if '@' in proxy else None
    proxy_ip, proxy_port = proxy.split('@')[1].split(':') if '@' in proxy else proxy.split(':')

    options = {
        'proxy'      : aiosocks.Socks5Addr(proxy_ip, proxy_port),
        'proxy_auth' : aiosocks.Socks5Auth(*auth) if auth else None,
        'dst'        : (host, port),
        'limit'      : 1024,
        'ssl'        : ssl._create_unverified_context() if use_ssl else None,
        'family'     : 2 # 2 = IPv4 | 10 = IPv6
    }

    reader, writer = await asyncio.wait_for(aiosocks.open_connection(**options), 15) # 15 second timeout

    while True:
        data  = await asyncio.wait_for(reader.readuntil(b'\r\n'), 300) # 5 minute timeout on no data received
        print(data.decode().strip()) # Print the response from the server
```

## [aiohttp](https://pypi.org/project/aiohttp)
```python
import asyncio
import aiohttp

async def proxy_example(proxy: str, url: str):
    '''Proxy can be in IP:PORT format or USER:PASS@IP:PORT format'''

    async with aiohttp.ClientSession() as session:
        async with session.get('https://google.com', proxy=f'http://{proxy}', timeout=15) as response:
            if response.status == 200: # 200 = success
                print(response.text()) # Print the response from the server
```

## [http.client](https://docs.python.org/3/library/http.client.html)
I really don't use this library much at all, so this is some LM generated function...

```python
import base64
import http.client

def proxy_example(proxy: str, url):
    '''Proxy can be in IP:PORT format or USER:PASS@IP:PORT format'''

    auth = proxy.split('@')[0].split(':') if '@' in proxy else None
    proxy_host, proxy_port = proxy.split('@')[1].split(':') if '@' in proxy else proxy.split(':')

    scheme, rest = url.split('://', 1)
    host, path = rest.split('/', 1)
    path = '/' + path
    
    if scheme == 'https':
        conn = http.client.HTTPConnection(proxy_host, proxy_port)
        conn.request('CONNECT', host)
        response = conn.getresponse()
        if response.status != 200:
            print("Failed to establish a tunnel via proxy.")
            print(response.status, response.reason)
            return
                conn = http.client.HTTPSConnection(proxy_host, proxy_port, context=None)
        conn.set_tunnel(host)
    else:
        conn = http.client.HTTPConnection(proxy_host, proxy_port)
        path = url

    headers = {}
    if auth:
        auth = base64.b64encode(f'{auth[0]}:{auth[1]}'.encode()).decode()
        headers['Proxy-Authorization'] = f'Basic {auth}'


    conn.request('GET', path, headers=headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    if response.status == 200:
        data = response.read()
        print(data.decode())

    conn.close()
```

## [requests](https://pypi.org/project/requests/)
```python
import requests

def proxy_example(proxy: str, url: str):
    '''Proxy can be in IP:PORT format or USER:PASS@IP:PORT format'''

    proxy_handler = {'http': 'http://'+proxy, 'https': 'https://'+proxy}
    response = requests.get(url, proxies=proxies)
    print(response.text)
```

## [urllib.request](https://docs.python.org/3/library/urllib.html)
```python
import urllib.request

def proxy_example(proxy: str, url: str):
    '''Proxy can be in IP:PORT format or USER:PASS@IP:PORT format'''

    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
    opener = urllib.request.build_opener(proxy_handler)

    if '@' in proxy: # Handle authentication
        creds, address = proxy.split('@')
        username, password = creds.split(':')
        auth_header = urllib.request.HTTPBasicAuthHandler()
        auth_header.add_password(realm=None, uri=proxy, user=username, passwd=password)
        opener.add_handler(auth_header)

    urllib.request.install_opener(opener)

    response = urllib.request.urlopen(url, timeout=15)
    if response.code == 200:
        print(response.read().decode())
```