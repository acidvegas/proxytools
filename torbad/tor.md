# Tor is NOT what you think it is


# Hardcoded "Directory Authorities" control all voting on the entire Tor network:
 - https://gitlab.torproject.org/tpo/core/tor/-/blob/main/src/app/config/auth_dirs.inc

# How many unique people are running relays

First let's analyze how many Relays ware on the network currently:
```
cat tor.json | jq -c .[] | wc -l
5828
```

Next, how many of these relays provide contact information:
```
cat tor.json | jq -c .[].contact | grep -v ^null | wc -l
4459
```

Let's now analyze the frequency of duplicate cntact information:
```
cat tor.json | jq -rc .[].contact | grep -v ^null | sort | uniq -c | sort -nr > relay_contact_frequency.txt
```

You can view these stats [here](./relay_contact_frequency.txt), but based on these results, some interesting observations are made:
- 435 relay operators are running more than 1 relay
- Almost 50 relay operators are running 10 or more relays