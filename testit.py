#!/usr/bin/env python3

# CL, 2025-11-05:
# installed packages
# Successfully installed certifi-2025.10.5 charset_normalizer-3.4.4 idna-3.11 requests-2.32.5 requests_sse-0.5.2 urllib3-2.5.0


# from https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service

import json
from requests_sse import EventSource

# Info: Wikipedia blocks Python scripts -> gives 403
# Fake Firefox -> gives 200
# self._kwargs['headers']['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'

kwargs = dict()
kwargs['headers'] = dict()
kwargs['headers']['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
url = 'https://stream.wikimedia.org/v2/stream/recentchange'
last_id = None
with EventSource(url,**kwargs) as stream:
    for event in stream:
        if event.type == 'message':
            try:
                change = json.loads(event.data)
            except ValueError:
                pass
            else:
                print(event.data)
                # discard canary events
                if change['meta']['domain'] == 'canary':
                    continue
                if change['user'] == 'Yourname':
                    print(change)
                    last_id = event.last_event_id
                    print(last_id)

# - Run this Python script.
# - Publish an edit to [[Sandbox]] on test.wikipedia.org, and observe it getting printed.
# - Quit the Python process.
# - Pass last_id to last_event_id parameter when creating the stream like
#   with EventSource(url,  latest_event_id=last_id) as stream: ...
# - Publish another edit, while the Python process remains off.
# - Run this Python script again, and notice it finding and printing the missed edit.
