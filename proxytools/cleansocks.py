#!/usr/bin/env python
# CleanSocks - Developed by acidvegas in Python (https://acid.vegas/proxytools)

'''
Requirements:
	PySocks (https://pypi.python.org/pypi/pysocks)

This script will clean a list of proxies by removing duplicates, checking for valid formats (IP:PORT), and testing if the proxies are working
'''

import argparse
import concurrent.futures
import os
import re
import sys

sys.dont_write_bytecode = True

def is_proxy(proxy):
	return re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):(?:6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{1,3}|[0-9])$', proxy)

def test_proxy(proxy):
	global good
	ip, port = proxy.split(':')
	try:
		sock = socks.socksocket()
		sock.set_proxy(socks.SOCKS5, ip, int(port))
		sock.settimeout(args.timeout)
		sock.connect(('www.google.com', 80))
	except:
		print('BAD  | ' + proxy)
	else:
		print('GOOD | ' + proxy)
		good.append(proxy)
	finally:
		sock.close()

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
proxies = set([line.strip() for line in open(args.input).readlines() if is_proxy(line)])
if not proxies:
	raise SystemExit('no proxies found from input file')
deduped, ips = list(), list()
for proxy in proxies:
	ip = proxy.split(':')[0]
	if ip not in ips:
		ips.append(ip)
		deduped.append(proxy)
deduped.sort()
good = list()
with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
	checks = {executor.submit(test_proxy, proxy): proxy for proxy in deduped}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
good.sort()
with open(args.output, 'w') as output_file:
	output_file.write('\n'.join(good))
print('Total : ' + format(len(proxies),           ',d'))
print('Good  : ' + format(len(good),              ',d'))
print('Bad   : ' + format(len(proxies)-len(good), ',d'))