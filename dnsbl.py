#!/usr/bin/env python
# DNSBL - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

# NOT FINISHED - WORK IN PROGRESS

import asyncio
import ipaddress
import socket

try:
    import aiodns
except ImportError:
    raise SystemExit('missing required library \'aiodns\' (https://pypi.org/project/aiodns/)')

DNSBL_LIST = [
    'b.barracudacentral.org',
    'cbl.abuseat.org',
    'http.dnsbl.sorbs.net',
    'misc.dnsbl.sorbs.net',
    'socks.dnsbl.sorbs.net',
    'web.dnsbl.sorbs.net',
    'dnsbl-1.uceprotect.net',
    'dnsbl-2.uceprotect.net',
    'dnsbl-3.uceprotect.net',
    'db.wpbl.info',
    'zen.spamhaus.org',
    'spam.dnsbl.sorbs.net',
    'noptr.spamrats.com',
    'cbl.anti-spam.org.cn',
    'dnsbl.dronebl.org',
    'dnsbl.inps.de',
    'dnsbl.sorbs.net',
    'drone.abuse.ch',
    'duinv.aupads.org',
    'dul.dnsbl.sorbs.net',
    'dyna.spamrats.com',
    'dynip.rothen.com',
    'ips.backscatterer.org',
    'ix.dnsbl.manitu.net',
    'korea.services.net',
    'orvedb.aupads.org',
    'osps.dnsbl.net.au',
    'osrs.dnsbl.net.au',
    'owfs.dnsbl.net.au',
    'pbl.spamhaus.org',
    'phishing.rbl.msrbl.net',
    'probes.dnsbl.net.au',
    'proxy.bl.gweep.ca',
    'rbl.interserver.net',
    'rdts.dnsbl.net.au',
    'relays.bl.gweep.ca',
    'relays.nether.net',
    'residential.block.transip.nl',
    'ricn.dnsbl.net.au',
    'rmst.dnsbl.net.au',
    'smtp.dnsbl.sorbs.net',
    'spam.abuse.ch',
    'spam.dnsbl.anonmails.de',
    'spam.rbl.msrbl.net',
    'spam.spamrats.com',
    'spamrbl.imp.ch',
    't3direct.dnsbl.net.au',
    'tor.dnsbl.sectoor.de',
    'torserver.tor.dnsbl.sectoor.de',
    'ubl.lashback.com',
    'ubl.unsubscore.com',
    'virus.rbl.jp',
    'virus.rbl.msrbl.net',
    'wormrbl.imp.ch',
    'xbl.spamhaus.org',
    'z.mailspike.net',
    'zombie.dnsbl.sorbs.net',
]

async def check_dnsbl(ip, dnsbl):
    reversed_ip = ipaddress.ip_address(ip).reverse_pointer
    try:
        resolver = aiodns.DNSResolver()
        lookup = f'{reversed_ip}.{dnsbl}'
        await resolver.query(lookup, 'A')
    except:
        return None

async def main(ip):
    tasks = [check_dnsbl(ip, dnsbl) for dnsbl in DNSBL_LIST]
    blacklisted_on = [res for res in await asyncio.gather(*tasks) if res]
    if blacklisted_on:
        print(f"{ip} is blacklisted on the following DNSBLs:")
        for bl in blacklisted_on:
            print(f"- {bl}")
    else:
        print(f"{ip} is not blacklisted on any known DNSBLs.")

if __name__ == "__main__":
    ip_address = input("Enter the IP address to check: ")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(ip_address))