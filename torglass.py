#!/usr/bin/env python
# Tor Glass - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''
A simple script to pull a list of all the Tor relays / exit nodes & generate a json database.

The example below will generate a map of all the Tor relays / exit nodes using the ipinfo.io API.
'''

try:
	import stem.descriptor.remote
except ImportError:
	raise SystemExit('missing required library \'stem\' (https://pypi.org/project/stem/)')

def get_descriptors() -> dict:
	''' Generate a json database of all Tor relays & exit nodes '''
	tor_map = {'relay':list(),'exit':list()}
	for relay in stem.descriptor.remote.get_server_descriptors():
		data = {
			'nickname'                    : relay.nickname,
			'fingerprint'                 : relay.fingerprint,
			'published'                   : str(relay.published) if relay.published else None,
			'address'                     : relay.address,
			'or_port'                     : relay.or_port,
			'socks_port'                  : relay.socks_port,
			'dir_port'                    : relay.dir_port,
			'platform'                    : str(relay.platform) if relay.platform else None,
			'tor_version'                 : str(relay.tor_version),
			'operating_system'            : relay.operating_system,
			'uptime'                      : relay.uptime,
			'contact'                     : str(relay.contact) if relay.contact else None,
			'exit_policy'                 : str(relay.exit_policy)    if relay.exit_policy    else None,
			'exit_policy_v6'              : str(relay.exit_policy_v6) if relay.exit_policy_v6 else None,
			'bridge_distribution'         : relay.bridge_distribution,
			'family'                      : list(relay.family) if relay.family else None,
			'average_bandwidth'           : relay.average_bandwidth,
			'burst_bandwidth'             : relay.burst_bandwidth,
			'observed_bandwidth'          : relay.observed_bandwidth,
			'link_protocols'              : relay.link_protocols,
			'circuit_protocols'           : relay.circuit_protocols,
			'is_hidden_service_dir'       : relay.is_hidden_service_dir,
			'hibernating'                 : relay.hibernating,
			'allow_single_hop_exits'      : relay.allow_single_hop_exits,
			'allow_tunneled_dir_requests' : relay.allow_tunneled_dir_requests,
			'extra_info_cache'            : relay.extra_info_cache,
			'extra_info_digest'           : relay.extra_info_digest,
			'extra_info_sha256_digest'    : relay.extra_info_sha256_digest,
			'eventdns'                    : relay.eventdns,
			'ntor_onion_key'              : relay.ntor_onion_key,
			'or_addresses'                : relay.or_addresses,
			'protocols'                   : relay.protocols
		}
		if relay.exit_policy.is_exiting_allowed():
			tor_map['exit'].append(data)
		else:
			tor_map['relay'].append(data)
	return tor_map


if __name__ == '__main__':
	import json

	print('loading Tor descriptors... (this could take a while)')
	tor_data = get_descriptors()
	
	with open('tor.json', 'w') as fd:
		json.dump(tor_data['relay'], fd)
	with open('tor.exit.json', 'w') as fd:
		json.dump(tor_data['exit'], fd)

	print('Relays: {0:,}'.foramt(len(tor_data['relay'])))
	print('Exits : {0:,}'.format(len(tor_data['exit'])))

	try:
		import ipinfo
	except ImportError:
		raise ImportError('missing optional library \'ipinfo\' (https://pypi.org/project/ipinfo/) for map visualization')
	
	try:
		handler = ipinfo.getHandler('changeme') # put your ipinfo.io API key here
		print('Relay Map: ' + handler.getMap([ip['address'] for ip in tor_data['relay']]))
		print('Exit  Map: ' + handler.getMap([ip['address'] for ip in tor_data['exit']]))
	except ipinfo.errors.AuthorizationError:
		print('error: invalid ipinfo.io API key (https://ipinfo.io/signup)')
	except Exception as ex:
		print(f'error generating ipinfo map ({ex})')