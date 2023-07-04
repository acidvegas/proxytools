#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

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

try:
	import dns.resolver
except ImportError:
	raise SystemExit('error: missing required \'dnspython\' library (https://pypi.org/project/dnspython/)')

# Globals
good    = list()
bad     = list()
unknown = list()
proxies = list()

blackholes = {
	'dnsbl.dronebl.org': {
		'2'  : 'Sample',
		'3'  : 'IRC Drone',
		'5'  : 'Bottler',
		'6'  : 'Unknown spambot or drone',
		'7'  : 'DDOS Drone',
		'8'  : 'SOCKS Proxy',
		'9'  : 'HTTP Proxy',
		'10' : 'ProxyChain',
		'11' : 'Web Page Proxy',
		'12' : 'Open DNS Resolver',
		'13' : 'Brute force attackers',
		'14' : 'Open Wingate Proxy',
		'15' : 'Compromised router / gateway',
		'16' : 'Autorooting worms',
		'17' : 'Automatically determined botnet IPs (experimental)',
		'18' : 'DNS/MX type'
	},
#	'rbl.efnetrbl.org': { # NOTE: Most IRC networks use DroneBL, un-comment this section to check the EFnetRBL
#		'1' : "Open Proxy",
#		'2' : "spamtrap666",
#		'3' : "spamtrap50",
#		'4' : "TOR",
#		'5' : "Drones / Flooding"
#	},
#	'torexit.dan.me.uk': { # TODO: The require a TXT lookup, although IRC daemons do numeric replies...will look into this
#		'E' : 'Exit',
#		'X' : 'Hidden Exit',
#		'A' : 'Authority',
#		'B' : 'BadExit',
#		'C' : 'NoEdConsensus',
#		'D' : 'V2Dir',
#		'F' : 'Fast',
#		'G' : 'Guard',
#		'H' : 'HSDir',
#		'N' : 'Named',
#		'R' : 'Running',
#		'S' : 'Stable',
#		'U' : 'Unnamed',
#		'V' : 'Valid'
#	}
}

def check(proxy):
	proxy_ip     = proxy.split(':')[0]
	formatted_ip = '.'.join(proxy_ip.split('.')[::-1])
	for blackhole in blackholes:
		try:
			results = dns.resolver.resolve(f'{formatted_ip}.{blackhole}', 'A')
			if results:
				for result in results:
					data  = result.to_text()
					reply = data.split('.')[-1:][0]
					if reply in blackholes[blackhole]:
						print(f'{proxy_ip.ljust(15)} \033[1;30m|\033[0m {blackhole.ljust(17)} \033[1;30m|\033[0m \033[1;31m{blackholes[blackhole][reply]}\033[0m')
						bad.append(proxy)
					else:
						print(f'{proxy_ip.ljust(15)} \033[1;30m|\033[0m {blackhole.ljust(17)} \033[1;30m|\033[0m Unknown ({data})')
						unknown.append(proxy)
			else:
				print(f'{proxy_ip.ljust(15)} \033[1;30m|\033[0m {blackhole.ljust(17)} \033[1;30m|\033[0m Error (No results)')
				unkown.append(proxy)
		except Exception as ex:
			print(f'{proxy_ip.ljust(15)} \033[1;30m|\033[0m {blackhole.ljust(17)} \033[1;30m|\033[0m \033[1;32mGOOD\033[0m')
	if proxy not in bad:
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
