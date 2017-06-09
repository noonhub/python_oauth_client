#!/usr/bin/env python
import argparse
import json
import time
import urllib
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urlparse import urlparse, parse_qs
import requests

config = None


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path != '/oauth/callback':
            return

        query_components = parse_qs(url.query)
        code = query_components.get('code')
        html = '<html><body>' \
               '<a href="JavaScript:window.close()">Close This Window And Return To Terminal</a>' \
               '</body></html>'
        code_for_token(code)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html)


class AsyncServer(Thread):
    def run(self):
        port = config.get('port')
        server = HTTPServer(('', port), RequestHandler)
        server.serve_forever()


def auth_url():
    params = {
        'client_id': config.get('client_id'),
        'scope': config.get('scopes'),
        'redirect_uri': config.get('redirect_uri'),
        'response_type': 'code',

    }
    return config['auth_url'] + '?' + urllib.urlencode(params)


def code_for_token(code):
    payload = {
        'code': code,
        'client_id': config.get('client_id'),
        'client_secret': config.get('client_secret'),
        'grant_type': 'authorization_code',
        'redirect_uri': config.get('redirect_uri')
    }
    response = requests.post('https://graph.facebook.com/oauth/access_token', data=payload)
    print("======== OAuth Credentials ========")
    print json.dumps(response.json(), indent=4, sort_keys=True)


def main():
    global config
    with open('config.json') as data_file:
        config = json.load(data_file)

    server = AsyncServer()
    server.daemon = True
    server.start()

    webbrowser.open_new(auth_url())

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
