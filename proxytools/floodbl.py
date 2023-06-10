#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

Test proxies against a set of Domain Name System-based Blackhole Lists (DNSBL) or Real-time Blackhole Lists (RBL)

'''

import argparse
import concurrent.futures
import os
import re
import socket

blackholes = ('dnsbl.dronebl.org','rbl.efnetrbl.org','torexit.dan.me.uk')

def check(proxy):
	ip  = proxy.split(':')[0]
	formatted_ip = '.'.join(ip.split('.')[::-1])
	for dnsbl in blackholes:
		try:
			socket.gethostbyname(f'{formatted_ip}.{dnsbl}')
		except socket.gaierror:
			print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + ip.ljust(22) + f'\033[30m({dnsbl})\033[0m')
			break
		else:
			print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + ip)
			good.append(proxy)

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
good = list()
with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
	checks = {executor.submit(check, proxy): proxy for proxy in proxies}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
good.sort()
with open(args.output, 'w') as output_file:
	output_file.write('\n'.join(good))
print('\n\033[34mTotal\033[0m : ' + format(len(proxies),         ',d'))
print('\033[34mGood\033[0m  : ' + format(len(good),              ',d'))
print('\033[34mBad\033[0m   : ' + format(len(proxies)-len(good), ',d'))