#!/usr/bin/env python
# Residential Proxy Usage Example - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''
Residential proxies are typically in a user:pass@host:port format, rotating on every request.

These example below show how to use these proxies with the aiosocks library and the requests library.
'''

import asyncio
import ssl

try:
    import aiosocks
except ImportError:
    raise SystemExit('missing required library \'aiosocks\' (https://pypi.org/project/aiosocks/)')

try:
    import requests
except ImportError:
    raise SystemExit('missing required library \'requestss\' (https://pypi.org/project/requests/)')

async def tcp_example(proxy: str, host: str, port: int, use_ssl: bool = False):
    '''
    Make a connection to a TCP server through a proxy.

    :param proxy: the proxy to use in the format of ip:port
    :param host: the host to connect to
    :param port: the port to connect to
    :param use_ssl: whether or not to use SSL
    '''
    auth = proxy.split('@')[0].split(':') if '@' in proxy else None
    proxy_ip, proxy_port = proxy.split('@')[1].split(':') if '@' in proxy else proxy.split(':')
    options = {
        'proxy'      : aiosocks.Socks5Addr(proxy_ip, proxy_port),
        'proxy_auth' : aiosocks.Socks5Auth(*auth) if auth else None,
        'dst'        : (host, port),
        'limit'      : 1024,
        'ssl'        : ssl._create_unverified_context() if use_ssl else None,
        'family'     : 2
    }
    reader, writer = await asyncio.wait_for(aiosocks.open_connection(**options), 15) # 15 second timeout
    while True:
        if reader.at_eof(): # Check if the connection has been closed
            break
        data  = await asyncio.wait_for(reader.readuntil(b'\r\n'), 300) # 5 minute timeout on no data received
        line  = data.decode('utf-8').strip()
        print(line) # Print the data received from the server

async def http_example(proxy: str, url: str):
     '''
     Make a HTTP request through a proxy.

     :param proxy: the proxy to use in the format of ip:port
     :param url: the url to request
     '''
     response = requests.get(url, proxies={'http': proxy, 'https':proxy}, timeout=15) # 15 second timeout
     return response.text