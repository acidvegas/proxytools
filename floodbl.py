#!/usr/bin/env python
# FloodBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

# This script will check a list of proxies aginst DNS Blackhole (DNSBL) lists to see if they are blackholed.
# Todo: Add support for asynchronous DNSBL lookups and proper IPv6 support.

import argparse
import concurrent.futures
import ipaddress
import os
import re

try:
	import dns.resolver
except ImportError:
	raise SystemExit('missing required \'dnspython\' library (https://pypi.org/project/dnspython/)')

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
		'18' : 'DNS/MX type',
		'19' : 'Abused VPN Service',
		'255': 'Uncategorzied threat class'
	},
	'rbl.efnetrbl.org': {
		'1' : "Open Proxy",
		'2' : "spamtrap666",
		'3' : "spamtrap50",
		'4' : "TOR",
		'5' : "Drones / Flooding"
	}
}

def check(proxy: str):
	'''
	Check if a proxy is blackholed.

	:param proxy: the proxy to check in the format of ip:port
	'''
	proxy_ip     = proxy.split(':')[0]
	formatted_ip = ipaddress.ip_address(proxy_ip).reverse_pointer
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
				unknown.append(proxy)
		except Exception as ex:
			print(f'{proxy_ip.ljust(15)} \033[1;30m|\033[0m {blackhole.ljust(17)} \033[1;30m|\033[0m \033[1;32mGOOD\033[0m')
	if proxy not in bad:
		good.append(proxy)


if __name__ == '__main__':
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
	proxies = set([proxy.split(':')[0] for proxy in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+', open(args.input).read(), re.MULTILINE)]) # TODO: handle IPv6 better

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
