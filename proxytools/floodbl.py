#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''
This script will test proxies against a set of Domain Name System-based Blackhole Lists (DNSBL) or Real-time Blackhole Lists (RBL)
'''

import argparse
import concurrent.futures
import os
import re
import socket

dnsbls = ('dnsbl.dronebl.org','rbl.efnetrbl.org','torexit.dan.me.uk')

def dnsbl_check(proxy):
	global good
	bad = False
	ip  = proxy.split(':')[0]
	formatted_ip = '.'.join(ip.split('.')[::-1])
	for dnsbl in dnsbls:
		try:
			socket.gethostbyname(f'{formatted_ip}.{dnsbl}')
		except socket.gaierror:
			pass
		else:
			bad = True
			break
	if bad:
		print('BAD  | ' + ip)
	else:
		good.append(proxy)
		print('GOOD | ' + ip)

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
	checks = {executor.submit(dnsbl_check, proxy): proxy for proxy in proxies}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
good.sort()
with open(args.output, 'w') as output_file:
	output_file.write('\n'.join(good))
print('Total : ' + format(len(proxies),           ',d'))
print('Good  : ' + format(len(good),              ',d'))
print('Bad   : ' + format(len(proxies)-len(good), ',d'))
