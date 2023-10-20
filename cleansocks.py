#!/usr/bin/env python
# CleanSocks - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)
# This script will clean a list of proxies by removing duplicates, checking for valid formats (IP:PORT), & testing if the proxies are working

import argparse
import asyncio
import aiofiles
import aiosocks
import os
import re
import signal
import sys

default_timeout = 10
default_threads = 16

all       = []
good      = []
print_bad = True
outfile = None

timeout = default_timeout
threads = default_threads

good_str = '\033[1;32mGOOD\033[0m \033[30m|\033[0m '
bad_str  = '\033[1;31mBAD\033[0m  \033[30m|\033[0m '

async def check(semaphore, proxy):
    async with semaphore:
        ip, port = proxy.split(':')
        test_host = 'www.google.com'
        test_port = 80
        options = {
            'proxy'      : aiosocks.Socks5Addr(proxy.split(':')[0], int(proxy.split(':')[1])),
            'proxy_auth' : None,
            'dst'        : (test_host, test_port),
            'limit'      : 1024,
            'ssl'        : None,
            'family'     : 2
        }
        try:
            await asyncio.wait_for(aiosocks.open_connection(**options), timeout)
        except OverflowError as e:
            print(bad_str + proxy)
            return
        except aiosocks.errors.SocksConnectionError as e:
            print(bad_str + proxy)
            return
        except aiosocks.errors.SocksError as e:
            print(bad_str + proxy)
            return
        except asyncio.exceptions.TimeoutError as e:
            print(bad_str + proxy)
            return
        except ConnectionResetError as e:
            print(bad_str + proxy)
            return
        except Exception as e:
            if print_bad:
                print(type(e))
                print(bad_str + proxy)
                return
        print(good_str + proxy)
        async with aiofiles.open(outfile, 'a') as good_file:
            await good_file.write(f"{proxy}\n")




async def main(targets):
    print('\033[34mTimeout\033[0m : ' + format(timeout, ',d'))
    print('\033[34mThreads\033[0m : ' + format(threads, ',d'))
    sema = asyncio.BoundedSemaphore(threads)
    jobs = []
    sub_jobs = []
    for target in targets:
        if len(sub_jobs) == threads:
            jobs.append(sub_jobs)
            sub_jobs.clear()
        sub_jobs.append(asyncio.create_task(check(sema, target)))
    for ct in range(0, len(jobs)):
        job_list = jobs[ct]
        await asyncio.gather(*job_list)


def signal_handler(sig, frame):
    print("\nExiting...")
    sys.exit(0)


def print_title():
    print('#'*56)
    print('#{0}#'.format(''.center(54)))
    print('#{0}#'.format('CleanSOCKS Proxy Cleaner'.center(54)))
    print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
    print('#{0}#'.format('https://git.acid.vegas/proxytools'.center(54)))
    print('#{0}#'.format(''.center(54)))
    print('#'*56)


def build_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s <input> <output> [options]')
    parser.add_argument('input', help='file to scan')
    parser.add_argument('output', help='file to output')
    parser.add_argument('-t', '--threads', 
            help=f'number of threads (default: {default_threads})', default=default_threads, type=int)
    parser.add_argument('-x', '--timeout', 
            help=f'socket timeout seconds (default: {default_timeout})',  default=default_timeout, type=int)
    return parser


if __name__ == '__main__':
    print_title()
    # register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    parser = build_parser()
    args = parser.parse_args()
    timeout = args.timeout
    threads = args.threads
    if not os.path.isfile(args.input):
        raise SystemExit('no such input file')
    outfile = args.output
    initial = len(open(args.input).readlines())
    ip_regex_str = '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+'
    proxies = set([proxy for proxy in re.findall(ip_regex_str, open(args.input).read(), re.MULTILINE)])
    if not proxies:
        raise SystemExit('no proxies found from input file')
    asyncio.run(main(proxies))
    good.sort()

