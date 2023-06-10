#!/usr/bin/env python
# SockSpot Proxy Scraper - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

import os
import re
import time
import urllib.request

github_list = (
	'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
	'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
	'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
	'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
	'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt',
	'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
    'https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
    'https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt',
	'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt',
	'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt',
	'https://spys.me/socks.txt'
)

def get_source(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
	source  = urllib.request.urlopen(req, timeout=5)
	return source.read().decode()

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('SockHub Proxy Scraper'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
bad_urls   = list()
dupes      = 0
proxy_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.txt')
proxy_list = list()
set(github_list)
print('scanning \033[35m{0:,}\033[0m urls from list...'.format(len(github_list)))
for url in github_list:
	try:
		source = get_source(url)
		found = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', source, re.MULTILINE)
		if found:
			print('found \033[93m{0:,}\033[0m proxies on \033[34m{1}\033[0m'.format(len(found), url))
			for proxy in found:
				if proxy not in proxy_list:
					proxy_list.append(proxy)
				else:
					dupes += 1
		else:
			print('no proxies found on ' + url)
	except:
		bad_urls.append(url)
if bad_urls:
	print('failed to load {0:,} urls'.format(len(bad_urls)))
	for url in bad_urls:
		print('failed to load ' + url)
if proxy_list:
	if dupes:
		print('found \033[32m{0:,}\033[0m total proxies! \033[30m({1:,} duplicates removed)\033[0m'.format(len(proxy_list), dupes))
	else:
		print('found \033[32m{0:,}\033[0m total proxies!'.format(len(proxy_list)))
	proxy_list.sort()
	with open (proxy_file, 'w') as proxy__file:
		for proxy in proxy_list:
			proxy__file.write(proxy + '\n')