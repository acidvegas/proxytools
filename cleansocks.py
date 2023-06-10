#!/usr/bin/env python
# CleanSocks - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

This script will clean a list of proxies by removing duplicates, checking for valid formats (IP:PORT), & testing if the proxies are working

'''

import argparse
import concurrent.futures
import os
import re

# Globals
good      = list()
print_bad = True

def check(proxy):
	ip, port = proxy.split(':')
	try:
		sock = socks.socksocket()
		sock.set_proxy(socks.SOCKS5, ip, int(port))
		sock.settimeout(args.timeout)
		sock.connect('www.google.com', 80)) # NOTE: use your own host instead in-case connections are blocked
	except:
		if print_bad:
			print('\033[1;31mBAD\033[0m  \033[30m|\033[0m ' + proxy)
	else:
		print('\033[1;32mGOOD\033[0m \033[30m|\033[0m ' + proxy)
		good.append(proxy)

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('CleanSOCKS Proxy Cleaner'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
parser = argparse.ArgumentParser(usage='%(prog)s <input> <output> [options]')
parser.add_argument('input',           help='file to scan')
parser.add_argument('output',          help='file to output')
parser.add_argument('-t', '--threads', help='number of threads      (default: 100)', default=100, type=int)
parser.add_argument('-x', '--timeout', help='socket timeout seconds (default: 15)',  default=15,  type=int)
args = parser.parse_args()
try:
	import socks
except ImportError:
	raise SystemExit('missing pysocks module (https://pypi.python.org/pypi/pysocks)')
if not os.path.isfile(args.input):
	raise SystemExit('no such input file')
initial = len(open(args.input).readlines())
proxies = set([proxy for proxy in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', open(args.input).read(), re.MULTILINE)])
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
