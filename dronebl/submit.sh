#!/bin/bash
# syntax: dronebl-submit.sh [bantype [host|IP|datafile [host|IP|datafile [etc.]]]
# where datafile contains one host or IP per line.
# This script will sort | uniq datafiles and query for existing active listings, so
# duplicate entries are no problem.
#
# dependencies: bash, wget, standard GNU utils (host / sed / grep / sort / etc)
#
# Version history:
# 2.1 -- fixed a logic error; removed the removal of /tmp/dronebl-*.xml files on error
# 2.0 -- completely rewritten for RPC2 (although argument syntax is backward-
# compatible)

RPCKEY="/etc/fail2ban/dronebl.rpckey"  # key, or path to file containing rpckey
REPORT_TO="https://dronebl.org/RPC2"

### end of user variables ###

if [ ! -w "/tmp" ]; then
	echo "Unable to write to /tmp.  Please ensure the disk is not full, and that this account has appropriate permissions."
	exit 1
fi

if [ -f "$RPCKEY" ]; then 
	if [ -r "$RPCKEY" ]; then
		RPCKEY=`cat $RPCKEY`
	else
		echo "RPC key in $RPCKEY is unreadable.  Exiting."
		exit 1
	fi
fi

function wash {  # wash <hostname> -- sets $IP by reference
	ADDR=$1
	TEST=`echo "${ADDR}." | grep -E "^([0-9]{1,3}\.){4}$"`
	if [ "$TEST" ]; then
		VALID=0
	else
		VALID=1
	fi

	if [ "$VALID" = "1" ]; then
		echo -n "Looking up $ADDR... "
		ADDR=`host $ADDR | grep -E -o -e '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'`
		TEST=`echo "${ADDR}." | grep -E "^([0-9]{1,3}\.){4}$"`
		if [ "$TEST" ]; then
			echo "$ADDR"
		else
			echo "Unable to resolve.  Skipping."
			return 1
		fi		
	fi
	eval "IP=$ADDR"
	return 0
}

function rinse {  # rinse <bantype> -- if bantype is contained in the deprecated list, exit
	DEPRECATED=( 4 11 12 )
	for dep in ${DEPRECATED[@]}; do
		if [ "$BANTYPE" == "$dep" ]; then
			echo "Bantype $BANTYPE has been deprecated.  The DroneBL is probably not the appropriate listing service for this sort of activity.  Please visit us on irc.atheme.org in #dronebl if you believe otherwise.  Exiting."
			exit 1
		fi
	done
}

function checkerror {  #checkerror <xmlfile> -- prints error messages from xml and exits
	ERROR=`grep -i error $1`
	if [ "$ERROR" ]; then
		ERROR=`grep '<code>' $1 | sed -r -e 's/<[^>]*>//g' -e 's/^\s*//g'`
		ERROR="$ERROR: `grep '<message>' $1 | sed -r -e 's/<[^>]*>//g' -e 's/^\s*//g'`"
		echo "The server returned an error ($ERROR) -- see /tmp/dronebl-query.xml and /tmp/dronebl-response.xml for full details."
		exit 1
	fi
}

if [ "$2" = "" ]; then
	echo -n 'Syntax:
'$0' [bantype [host|IP|datafile [host|IP|datafile [etc.]]]]

Types are as follows:
2 = Sample
3 = IRC Drone
4 = Tor exit node (deprecated)
5 = Bottler
6 = Unknown spambot or drone
7 = DDOS Drone
8 = SOCKS Proxy
9 = HTTP Proxy
10 = ProxyChain
11 = Machines and netblocks compromised or owned by MediaDefender (deprecated)
12 = Trolls (deprecated)
13 = Brute force attackers
14 = Open Wingate
15 = Open Router
255 = Unknown

Which type? '
	read BANTYPE
	rinse $BANTYPE
	echo -n "What's the hostname / IP address? "
	read ADDR
	wash $ADDR
	if [ $? ]; then
		IPLIST[0]=$IP
	else
		echo "Unable to resolve $ADDR.  Exiting."
		exit 1
	fi
else
	rinse $1
	args=($@)
	echo "A little housekeeping..."
	for (( x=1; x<${#args[@]}; x++ )); do
		if [ "${args[$x]}" != "" ]; then
			filename="${args[$x]}"
			if [ ! -r "$filename" ]; then filename="$PWD/${args[$x]}"; fi
			if [ -r "$filename" ]; then
				for i in `sort -u $PWD/${args[$x]}`; do
					wash $i
					if [ $? ]; then IPLIST[${#IPLIST[@]}]=$IP; fi
				done
			else
				wash ${args[$x]}
				if [ $? ]; then IPLIST[${#IPLIST[@]}]=$IP; fi
			fi
		fi
	done
	IPLIST=( `for (( x=0; x<${#IPLIST[@]}; x++ )) ; do echo ${IPLIST[$x]}; done | sort -u` )
	BANTYPE=$1
fi

POSTFILE="/tmp/dronebl-query.xml"
RESPONSEFILE="/tmp/dronebl-response.xml"

echo "Housekeeping finished.  Working with ${#IPLIST[@]} unique, valid addresses."
if [ ${#IPLIST[@]} -eq 0 ]; then
	echo "No hosts to report.  Exiting."
	exit 0
fi

echo "Checking for exiting entries... "
echo "<?xml version=\"1.0\"?>
<request key='"$RPCKEY"'>" >$POSTFILE
for i in ${IPLIST[@]}; do
	echo "	<lookup ip='$i' />" >>$POSTFILE
done
echo "</request>" >>$POSTFILE
wget -q --post-file="$POSTFILE" -O "$RESPONSEFILE" --header="Content-Type: text/xml" $REPORT_TO
checkerror $RESPONSEFILE
grepfor='type="'$BANTYPE'"'
for i in `grep 'listed="1"' $RESPONSEFILE | grep $grepfor | grep -E -o -e '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | sort -u`; do
	IPLIST=( ${IPLIST[@]%%$i} )
	echo "$i is already active in the DroneBL database as ban type $BANTYPE.  Removing."
done

if [ ${#IPLIST[@]} -eq 0 ]; then
	echo "No hosts to report.  Exiting."
	exit 0
elif [ ${#IPLIST[@]} -eq 1 ]; then
	echo -n "Reporting ${IPLIST[@]} as ban type $BANTYPE... "
else
	echo -n "Reporting ${#IPLIST[@]} hosts as ban type $BANTYPE... "
fi
echo "<?xml version=\"1.0\"?>
<request key='"$RPCKEY"'>" >$POSTFILE
for i in ${IPLIST[@]}; do
	if [ "`echo ${i}. | grep -E '^([0-9]{1,3}\.){4}$'`" != "" ]; then echo "	<add ip='$i' type='$BANTYPE' />" >>$POSTFILE; fi
done
echo "</request>" >>$POSTFILE
wget -q --post-file="$POSTFILE" -O "$RESPONSEFILE" --header="Content-Type: text/xml" $REPORT_TO
checkerror $RESPONSEFILE
echo "done."
rm -f /tmp/dronebl*.xml
exit 0
