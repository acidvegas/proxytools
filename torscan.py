#!/usr/bin/env python
# Tor Scan - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

'''

PUll a list of information about all Tor relays & exit relays into a json database

'''

import json

try:
	import stem.descriptor.remote
except ImportError:
	raise SystemExit('missing required library \'stem\' (https://pypi.org/project/stem/)')

tor_map = {'relay':list(),'exit':list()}

for relay in stem.descriptor.remote.get_server_descriptors().run():
	_map = {
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
		tor_map['exit'].append(_map)
	else:
		tor_map['relay'].append(_map)
with open('tor.out', 'w') as fd:
	json.dump(tor_map['relay'], fd)
with open('tor.exit.out', 'w') as fd:
	json.dump(tor_map['exit'], fd)