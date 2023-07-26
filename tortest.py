#!/usr/bin/env python
# Tor Test - Developed by acidvegas in Python (https://git.acid.vegas/proxytools)

import io
import time

try:
    import pycurl
except ImportError:
     raise Exception('missing required library \'pycurl\' (https://pypi.org/project/pycurl/)')

try:
    import stem.control
except ImportError:
    raise Exception('missing required library \'stem\' (https://pypi.org/project/stem/)')

# Globals
EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442' # https://metrics.torproject.org/rs.html#details/379FB450010D17078B3766C2273303C358C3A442
SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

def query(url):
    ''' Uses pycurl to fetch a site using the proxy on the SOCKS_PORT. '''
    output = io.StringIO.StringIO()
    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    query.setopt(pycurl.WRITEFUNCTION, output.write)
    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        raise ValueError("Unable to reach %s (%s)" % (url, exc))

def scan(controller, path):
    ''' Test the connection to a website through the given path of relays using the given controller '''
    circuit_id = controller.new_circuit(path, await_build = True)
    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, circuit_id)
    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')    # leave stream management to us
        start_time = time.time()
        check_page = query('https://check.torproject.org/')
        if 'Congratulations. This browser is configured to use Tor.' not in check_page:
            raise ValueError("Request didn't have the right content")
        return time.time() - start_time
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')

# Main
with stem.control.Controller.from_port(port=9056) as controller:
    controller.authenticate('loldongs')
    relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]
    for fingerprint in relay_fingerprints:
        try:
            time_taken = scan(controller, [fingerprint, EXIT_FINGERPRINT])
            print('%s => %0.2f seconds' % (fingerprint, time_taken))
        except Exception as exc:
            print('%s => %s' % (fingerprint, exc))