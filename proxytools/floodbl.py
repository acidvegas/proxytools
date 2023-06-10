#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

Test proxies against a set of Domain Name System-based Blackhole Lists (DNSBL) or Real-time Blackhole Lists (RBL)

'''

import asyncio
import argparse
import os
import re
import socket

blackholes = ('dnsbl.dronebl.org','rbl.efnetrbl.org','torexit.dan.me.uk')

async def check(sema, proxy):
	async with sema:
		ip  = proxy.split(':')[0]
		formatted_ip = '.'.join(ip.split('.')[::-1])
		for dnsbl in blackholes:
			try:
				socket.gethostbyname(f'{formatted_ip}.{dnsbl}')
				print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + ip)
				good.append(proxy)
			except socket.gaierror:
				print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + ip.ljust(22) + f'\033[30m({dnsbl})\033[0m')
				break

async def main(proxies, threads):
	sema = asyncio.BoundedSemaphore(threads) # B O U N D E D   S E M A P H O R E   G A N G
	jobs = list()
	for proxy in proxies:
		jobs.append(asyncio.ensure_future(check(sema, proxy)))
	await asyncio.gather(*jobs)

# Main
parser = argparse.ArgumentParser(usage='%(prog)s <input> <output> [options]')
parser.add_argument('input',           help='file to scan')
parser.add_argument('output',          help='file to output')
parser.add_argument('-t', '--threads', help='number of threads (default: 100)', default=100, type=int)
args = parser.parse_args()
if not os.path.isfile(args.input):
	raise SystemExit('no such input file')
proxies = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', open(args.input).read(), re.MULTILINE)
if not proxies:
	raise SystemExit('no proxies found from input file')
asyncio.run(main(proxies, args.threads))
good.sort()
with open(args.output, 'w') as output_file:
	output_file.write('\n'.join(good))
print('\n\033[34mTotal\033[0m : ' + format(len(proxies),         ',d'))
print('\033[34mGood\033[0m  : ' + format(len(good),              ',d'))
print('\033[34mBad\033[0m   : ' + format(len(proxies)-len(good), ',d'))