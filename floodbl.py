#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

Test proxies against a set of Domain Name System-based Blackhole Lists (DNSBL) or Real-time Blackhole Lists (RBL)

'''

'''
Notes for future improvement:

To query an IPv6 address, you must expand it, then reverse it into "nibble" format.
    e.g. if the IP was 2001:db8::1, you expand it to 2001:0db8:0000:0000:0000:0000:0000:0001 and reverse it.
    In nibble format it is 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2 and add on the dns blacklist you require.

        e.g.   1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.tor.dan.me.uk

    If the IP has a match, the DNS server will respond with an "A" record of 127.0.0.100.
    It will also respond with a "TXT" record with extra information as per below:

        N:<nodename>/P:<port1[,port2]>/F:<flags>

    port1 is the OR (onion router) port, port2 (if specified) is the DR (directory) port.
    Flags are defined as follows:

        E     Exit
        X     Hidden Exit
        A     Authority
        B     BadExit
        C     NoEdConsensus
        D     V2Dir
        F     Fast
        G     Guard
        H     HSDir
        N     Named
        R     Running
        S     Stable
        U     Unnamed
        V     Valid
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
