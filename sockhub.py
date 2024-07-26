#!/usr/bin/env python
# SockHub Proxy Scraper - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''
There is a file in this repository called proxy_sources.txt which contains a list of URLs to scrape for proxies.
This list it not maintained and may contain dead links or links to sites that no longer contain proxies.
'''

import concurrent.futures
import logging
import os
import re
import urllib.request

# Global
proxies = list()

def find_proxies(url: str) -> str:
	'''
	Check a URL for IP:PORT proxies.

	:param url: The URL to check for proxies.
	'''

	global proxies

	try:
		source = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'SockHub/1.0'})).read().decode()
		if source:
			found = set(re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', source, re.MULTILINE))
			if (new_proxies := [proxy for proxy in found if proxy not in proxies]):
				proxies += new_proxies
				print(f'found \033[32m{len(found):,}\033[0m new proxies on \033[34m{url}\033[0m')
		else:
			logging.warning(f'found \033[31m0\033[0m new proxies on \033[34m{url}\033[0m \033[30m(source is empty)\033[0m')
	except Exception as ex:
		logging.error(f'found \033[31m0\033[0m new proxies on \033[34m{url}\033[0m \033[30m({ex})\033[0m')


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='SockHub Proxy Scraper - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)')
	parser.add_argument('-i', '--input',  help='input file containing a list of URLs to scrape (one per line) or a single URL')
	parser.add_argument('-o', '--output', help='output file to save proxies to', default='proxies.txt')
	parser.add_argument('-c', '--concurrency', help='number of concurrent threads to use (default: 10)', default=10, type=int)
	args = parser.parse_args()

	logging.basicConfig(format='%(message)s', level=logging.INFO)

	if not os.path.isfile(args.input):
		if args.input.startswith('https://') or args.input.startswith('http://'):
			logging.info('using input as a single url...')
			proxy_sources = [args.input]
		else:
			logging.fatal('input file does not exist!')

	proxy_sources = open(args.input, 'r').read().split('\n')

	if not proxy_sources:
		logging.fatal('proxy sources input file is empty!')

	logging.debug('scanning \033[35m{len(urls):,}\033[0m urls from list...')

	with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
		futures = [executor.submit(find_proxies, url) for url in proxy_sources]
	concurrent.futures.wait(futures)

	if proxies:
		logging.info('found \033[32m{len(proxies):,}\033[0m total proxies!')
		proxies.sort()
		with open (args.output, 'w') as output_file:
			for proxy in proxies:
				output_file.write(proxy + '\n')
	else:
		logging.warning('no proxies found!')
