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
good       = list()
proxies    = list()
print_bad  = True

def check(proxy):
	formatted_ip = '.'.join(proxy.split('.')[::-1])
	for blackhole in blackholes:
		try:
			socket.gethostbyname(f'{formatted_ip}.{blackhole}')
		except socket.gaierror:
			if print_bad:
				print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + proxy.ljust(22) + f'\033[30m({blackhole})\033[0m')
			break
		else:
			print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + proxy)
			good.append(proxy)

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('FloodBL Blackhole Checker'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
parser = argparse.ArgumentParser(usage='%(prog)s <input> <output> [options]')
parser.add_argument('input',           help='file to scan')
parser.add_argument('output',          help='file to output')
parser.add_argument('-t', '--threads', help='number of threads (default: 100)', default=100, type=int)
args = parser.parse_args()
if not os.path.isfile(args.input):
	raise SystemExit('no such input file')
initial = len(open(args.input).readlines())
proxies = set([proxy.split(':')[0] for proxy in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', open(args.input).read(), re.MULTILINE)])
if not proxies:
	raise SystemExit('no proxies found from input file')
with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
	checks = {executor.submit(check, proxy): proxy for proxy in proxies}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
good.sort()
with open(args.output, 'w') as output_file:
	output_file.write('\n'.join(good))
print('\033[34mTotal\033[0m : ' + format(len(proxies),           ',d'))
print('\033[34mGood\033[0m  : ' + format(len(good),              ',d'))
print('\033[34mBad\033[0m   : ' + format(len(proxies)-len(good), ',d'))
print('\033[34mDupe\033[0m  : ' + format(initial-len(proxies),   ',d'))
