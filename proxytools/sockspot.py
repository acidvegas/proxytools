#!/usr/bin/env python
# SockSpot - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

import datetime
import json
import base64
import os
import re
import threading
import time
import urllib.request

# Blogspot URLs
blogspot_list = (
	'live-socks.net',
	'newfreshproxies-24.blogspot.sg',
	'proxyserverlist-24.blogspot.sg',
	'socks24.org',
	'sock5us.blogspot.com',
	'sockproxy.blogspot.com',
	'socksproxylist24.blogspot.com',
	'newsocks.info',
	'socksecurelist.ca',
	'canada-socks247.com',
	'sock5us.blogspot.com',
	'socks24.org',
	'sslproxies24.blogspot.com',
	'vip-socks24.blogspot.com'
)

# Settings
max_results = 100 # Maximum number of results per-page.
post_depth  = 1   # How many days back from the current date to pull posts from. (1 = Today Only)
timeout     = 30  # Timeout for HTTP requests.

# Globals
proxy_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.txt')
proxy_list = list()
threads    = dict()

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason):
	print(f'{get_time()} | [!] - {msg} ({reason})')

def get_time():
	return time.strftime('%I:%M:%S')

def get_date():
	date = datetime.datetime.today()
	return '{0}-{1:02d}-{2:02d}'.format(date.year, date.month, date.day)

def get_date_range():
	date_range = datetime.datetime.today() - datetime.timedelta(days=post_depth)
	return '{0}-{1:02d}-{2:02d}'.format(date_range.year, date_range.month, date_range.day)

def get_source(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
	source  = urllib.request.urlopen(req, timeout=timeout)
	charset = source.headers.get_content_charset()
	if charset:
		return source.read().decode(charset)
	else:
		return source.read().decode()

def parse_blogspot(url):
	global proxy_list
	try:
		source = json.loads(get_source(f'http://{url}/feeds/posts/default?max-results={max_results}&alt=json&updated-min={get_date_range()}T00:00:00&updated-max={get_date()}T23:59:59&orderby=updated'))
		found  = []
		if source['feed'].get('entry'):
			for item in source['feed']['entry']:
				data    = item['content']['$t']
				proxies = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', data, re.MULTILINE)
				if proxies:
					found      += proxies
					proxy_list += proxies
			debug('Found {0} proxies on {1}'.format(format(len(found), ',d'), url))
		else:
			error('No posts found on page!', url)
	except Exception as ex:
		proxy_value = ex

def scan_blogspots():
	for url in blogspot_list:
		threads[url] = threading.Thread(target=parse_blogspot, args=(url,))
	for thread in threads:
		threads[thread].start()
		time.sleep(10)
	for thread in threads:
		threads[thread].join()
	debug('Found {0} total proxies!'.format(format(len(proxy_list), ',d')))
	with open (proxy_file, 'w') as proxy__file:
		for proxy in proxy_list:
			proxy__file.write(proxy + '\n')

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('SockSpot Proxy Scraper'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
debug(f'Scanning {len(blogspot_list)} URLs from list...')
threading.Thread(target=scan_blogspots).start()
for url in blogspot_list:
	threads[url] = threading.Thread(target=parse_blogspot, args=(url,))
for thread in threads:
	threads[thread].start()
	time.sleep(10)
for thread in threads:
	threads[thread].join()
if proxy_value == 0:
	error('no socks found')
debug('Found {0} total proxies!'.format(format(len(proxy_list), ',d')))
with open (proxy_file, 'w') as proxy__file:
	for proxy in proxy_list:
		proxy__file.write(proxy + '\n')
