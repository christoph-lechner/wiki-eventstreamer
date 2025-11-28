# C. Lechner, 2025-Nov-27
#
# Tests for HTTP health monitoring class

import time
from healthcheck import Healthcheck
import requests

hc_kwargs = {
    'http_port': 44444,
    'max_age': 5,
}
check_url = 'http://localhost:44444/check'

def test_create():
    h = Healthcheck(**hc_kwargs)

def test_runserver():
    h = Healthcheck(**hc_kwargs)
    h.start_server()
    time.sleep(1)
    h.stop_server()

#########################################
### tests that send GET/HEAD requests ###
#########################################

# behavior before first heartbeat is send
def test_wd_before_first_heartbeat():
    h = Healthcheck(**hc_kwargs)
    h.start_server()

    # allow for the server to start up
    time.sleep(1)

    # get status WITHOUT sending any heartbeat -> expect "health not OK"
    r = requests.get(check_url)
    assert r.status_code==500

    h.stop_server()

def test_wd_corefunction():
    def worker(method='get'):
        def req(method):
            if method=='get':
                return requests.get(check_url)
            elif method=='head':
                return requests.head(check_url)
            else:
                raise ValueError(f'unexpected method {method}')

        h = Healthcheck(**hc_kwargs)
        h.start_server()
        h.heartbeat()
        # give it some time to start before testing commences
        time.sleep(1)

        # Test 1: expect "health OK"
        r = req(method)
        assert r.status_code==200

        time.sleep(10)

        # Test 2: expect "health not OK"
        r = req(method)
        assert r.status_code==500

        # send heartbeat and short delay (we don't want to measure propagation time of heartbeat to HTTP server)
        h.heartbeat()
        time.sleep(1)

        # Test 3: expect "health OK"
        r = req(method)
        assert r.status_code==200

        h.stop_server()

    worker(method='get')
    worker(method='head')


