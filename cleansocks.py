#!/usr/bin/env python
# CleanSocks - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

# This script will clean a list of proxies by removing duplicates, checking for valid formats (IP:PORT), & testing if the proxies are working
# If a proxy is found working on multiple ports, we will only store the first working port to avoid ip duplication in the clean results.

import argparse
import asyncio
import os
import re

try:
	import aiosocks
except ImportError:
	raise SystemExit('missing pysocks module (https://pypi.org/project/aiosocks/)')

try:
	import aiohttp
except ImportError:
	raise SystemExit('missing pysocks module (https://pypi.org/project/aiosocks/)')

# Globals
all  = list()
good = list()

async def check_http_proxy(semaphore: asyncio.Semaphore, proxy: str):
	'''
	Checks if a HTTP proxy is working.
	
	:param semaphore: The semaphore to use.
	:param proxy: The proxy to check.
	'''
	async with semaphore:
		proxy_ip = proxy.split(':')[0]
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get('https://google.com', proxy=f'http://{proxy}', timeout=args.timeout) as response:
					if response.status == 200:
						print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + proxy)
						if proxy_ip not in all:
							all.append(proxy_ip)
							good.append(proxy)
					else:
						if args.bad:
							print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + proxy)
			except:
				if args.bad:
					print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + proxy)

async def check_socks_proxy(semaphore: asyncio.Semaphore, proxy: str):
	'''
	Checks if a SOCKS proxy is working.
	
	:param semaphore: The semaphore to use.
	:param proxy: The proxy to check.
	'''
	async with semaphore:
		proxy_ip, proxy_port = proxy.split(':')
		options = {
			'proxy'      : aiosocks.Socks5Addr(proxy_ip, proxy_port),
			'proxy_auth' : None,
			'dst'        : ('www.google.com', 80),
			'limit'      : 1024,
			'ssl'        : None,
			'family'     : 2
		}
		try:
			await asyncio.wait_for(aiosocks.open_connection(**options), args.timeout)
		except:
			if args.bad:
				print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + proxy)
		else:
			print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + proxy)
			if proxy_ip not in all:
				all.append(proxy_ip)
				good.append(proxy)

async def main(targets):
	'''
	Starts the main event loop.
	
	:param targets: The proxies to check.
	'''
	sema = asyncio.BoundedSemaphore(args.threads)
	jobs = list()
	for target in targets:
		if args.socks:
			jobs.append(asyncio.ensure_future(check_socks_proxy(sema, target)))
		else:
			jobs.append(asyncio.ensure_future(check_http_proxy(sema, target)))
	await asyncio.gather(*jobs)


if __name__ == '__main__':
	print('#'*56)
	print('#{0}#'.format(''.center(54)))
	print('#{0}#'.format('CleanSOCKS Proxy Cleaner'.center(54)))
	print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
	print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
	print('#{0}#'.format(''.center(54)))
	print('#'*56)

	parser = argparse.ArgumentParser(usage='%(prog)s <input> <output> [options]')
	parser.add_argument('input', help='file to scan')
	parser.add_argument('output', help='file to output')
	parser.add_argument('-s', '--socks', action='store_true', help='Check SOCKS proxies (default: HTTP)')
	parser.add_argument('-b', '--bad', action='store_true', help='Show bad proxies')
	parser.add_argument('-t', '--threads', help='number of threads      (default: 100)', default=100, type=int)
	parser.add_argument('-x', '--timeout', help='socket timeout seconds (default:  15)', default=15, type=int)
	args = parser.parse_args()

	if not os.path.isfile(args.input):
		raise SystemExit('no such input file')

	initial = len(open(args.input).readlines())
	proxies = set([proxy for proxy in re.findall(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', open(args.input).read(), re.MULTILINE)])

	if not proxies:
		raise SystemExit('no proxies found from input file')


	print('\033[1;32mChecking {0:,} {1} proxies using {2:,} threads... \033[1;30m(Pass the -h or --help argument to change these settings)\033[0m'.format(len(proxies), 'SOCKS' if args.socks else 'HTTP', args.threads))
	asyncio.run(main(proxies))

	good.sort()

	with open(args.output, 'w') as output_file:
		output_file.write('\n'.join(good))
	
	print('\033[34mTotal\033[0m : ' + format(len(proxies),           ',d'))
	print('\033[34mGood\033[0m  : ' + format(len(good),              ',d'))
	print('\033[34mBad\033[0m   : ' + format(len(proxies)-len(good), ',d'))
	print('\033[34mDupe\033[0m  : ' + format(initial-len(proxies),   ',d'))
