#!/usr/bin/env python
# SockSpot Proxy Scraper - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

Scrap IP:PORT proxies from a URL list

'''

import concurrent.futures
import os
import re
import time
import urllib.request

# Can be any URL containing a list of IP:PORT proxies (does not have to be socks5)
# The current list contains proxy sources that are updated frequently with new proxies
# Almost all of the Github repos pull from the same place & contain duplicates (which are removed)
urls = set((
	'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt',
	'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt',
	'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
	'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt',
	'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
	'https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt',
	'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt',
	'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
	'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt',
	'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt',
	'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
	'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt',
	'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt',
	'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks5.txt',
	'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
	'https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt',
	'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
	'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
	'https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt',
	'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt',
	'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt',
	'https://api.openproxylist.xyz/socks5.txt',
	'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5',
	'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5',
	'https://proxyscan.io/download?type=socks5',
	'https://proxyspace.pro/socks5.txt',
	'https://spys.me/socks.txt'
))

def get_source(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
	source  = urllib.request.urlopen(req, timeout=10)
	return source.read().decode()

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('SockHub Proxy Scraper'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
total = 0
proxies = list()
proxy_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.txt')
print('scanning \033[35m{0:,}\033[0m urls from list...'.format(len(urls)))
for url in urls: # TODO: Maybe add concurrent.futures support for using larger lists
	try:
		source = get_source(url)
	except:
		print('found \033[31m0\033[0m new proxies on \033[34m{0}\033[0m \033[30m(failed to load)\033[0m'.format(url))
	else:
		total+= len(source.split())
		found = set([proxy for proxy in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', source, re.MULTILINE) if proxy not in proxies])
		if found:
			proxies += found
			print('found \033[32m{0:,}\033[0m new proxies on \033[34m{1}\033[0m'.format(len(found), url))
		else:
			print('found \033[31m0\033[0m new proxies on \033[34m{0}\033[0m \033[30m(duplicates)\033[0m'.format(url))
if proxies:
	if len(proxies) < total:
		print('found \033[32m{0:,}\033[0m total proxies! \033[30m({1:,} duplicates removed)\033[0m'.format(len(proxies), total-len(proxies)))
	else:
		print('found \033[32m{0:,}\033[0m total proxies!'.format(len(proxies)))
	proxies.sort()
	with open (proxy_file, 'w') as proxy__file:
		for proxy in proxies:
			proxy__file.write(proxy + '\n')