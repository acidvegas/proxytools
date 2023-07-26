#!/bin/bash
#################################################################################
## checkdnsbl.sh by rojo (rojo @ headcandy.org) and
## outsider (outsider @ scarynet.org) and
## remco (remco @ webconquest.com)
##
## LICENSE AGREEMENT
## By using this script, you are implying acceptance of the idea that this script
## is a stimulating piece of prose.  As such, PLEASE DO NOT PLAGIARIZE IT.  As
## long as you give me credit for my work, feel free to redistribute / make a
## profit / rewrite / whatever you wish to the script.  Just don't mess it up
## and pretend that the bug was my fault.  My code is bug-free, dammit!
##
## syntax: /usr/local/sbin/checkdnsbl.sh ip_addr
## where ip_addr is a valid four-octet IPv4 address
## * exits 0 if a match is found; exits 1 for no match
## * intended to be called from /etc/hosts.deny via aclexec
##
## example hosts.deny:
#
# sshd : 10.0.0.0/24, 127.0.0.1 : allow
# ALL : 192.168.0.0/32 : deny
# ALL EXCEPT httpd : ALL : aclexec /usr/local/sbin/checkdnsbl %a
#
## This will deny connections from DNSBL-flagged hosts, and assume the rest are
## safe.  MAKE SURE THAT THIS SCRIPT IS RUN AFTER ALL EXPLICITLY DEFINED
## ADDRESSES!  After tcpwrappers spawns this script, the connection is either
## passed or failed, with no further rule matching.
##
## As of the writing of this script, aclexec in hosts.allow allows every client
## to connect, regardless of returned exit code.  This script will NOT work if
## called from hosts.allow.  It should only be called from hosts.deny.
##
## To test whether this script works, try binding to a banned address.  Both
## dronebl.org and spamhaus.org, for example, include 127.0.0.2 in their
## databases for testing.  So, if this script monitors ssh connections, and such
## a service exists in your array of DNSBL hosts, try the following command:
# ssh -o BindAddress=127.0.0.2 localhost
## If all works as intended, you should see "ssh_exchange_identification:
## Connection closed by remote host."  And so will other blacklisted clients.
#################################################################################

# DNSBL[x] -- array of DNSBL hosts to query
DNSBL[0]="dnsbl.dronebl.org"
DNSBL[1]="rbl.efnetrbl.org"
DNSBL[2]="dnsbl.swiftbl.net"
DNSBL[3]="combined.abuse.ch"
DNSBL[4]="bogons.cymru.com"


# Number of minutes to cache queries
QUERY_EXPIRE=5

# Location for cache
CACHE_FOLDER="/tmp/checkdnsbl"

# UMASK value for created files and directory
UMASK="077"

################################# stop editing ##################################

IPADDR=`echo $1 | sed -r -e 's/^::ffff://'`
IP_BACKWARD=`host $IPADDR|grep -E -o -e '[0-9a-f\.]+\.(in-addr|ip6)\.arpa'|sed -r -e 's/\.i.+$//'`

umask $UMASK

if [ ! -d "$CACHE_FOLDER" ]; then mkdir $CACHE_FOLDER;
elif [ -f "$CACHE_FOLDER/$IPADDR-0" ]; then {
	echo CACHED: $IPADDR found in `cat $CACHE_FOLDER/$IPADDR-0`
	exit 0
};
elif [ -f "$CACHE_FOLDER/$IPADDR-1" ]; then {
	echo CACHED: $IPADDR not found in any DNSBLs.
	exit 1
}; fi

for (( x=0; x<${#DNSBL[@]}; x++ )); do {
	DNSBLQUERY=$IP_BACKWARD.${DNSBL[$x]}
	echo -n "checking $DNSBLQUERY... "
	DNSBLOUT=`host $DNSBLQUERY | grep -E -o -e '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'`
	if [ "$DNSBLOUT" != "" ]; then
		echo "MATCH: $DNSBLOUT"
		echo "${DNSBL[$x]} : $DNSBLOUT" >>$CACHE_FOLDER/$IPADDR-0
		sleep $(( $QUERY_EXPIRE * 60 )) && {
			rm -f $CACHE_FOLDER/$IPADDR-0
		} &
		exit 0
 	else
 		echo "no match."
	fi
}; done
touch $CACHE_FOLDER/$IPADDR-1
sleep $(( $QUERY_EXPIRE * 60 )) && {
	rm -f $CACHE_FOLDER/$IPADDR-1
} &
exit 1
