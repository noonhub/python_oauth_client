#!/usr/bin/env python
from argparse import ArgumentParser
import json
from os import path
import time
import urllib
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urlparse import urlparse, parse_qs
import requests

config = None
provider = 'uber'

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path != '/oauth/callback':
            return

        query_components = parse_qs(url.query)
        code = query_components.get('code')
        html = '<html><body>' \
               '<h1 style="text-align: center;">' \
               '<a href="JavaScript:window.close()">Close This Window And Return To Terminal</a>' \
               '</h1>' \
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


def code_for_token(code):
    payload = {
        'code': code,
        'client_id': config.get(provider).get('client_id'),
        'client_secret': config.get(provider).get('client_secret'),
        'grant_type': 'authorization_code',
        'redirect_uri': config.get('redirect_uri')
    }
    response = requests.post(config.get(provider).get('token_url'), data=payload)

    print(response)
    print("======== OAuth Credentials ========")
    print json.dumps(response.json(), indent=4, sort_keys=True)


def auth_url():
    params = {
        'client_id': config.get(provider).get('client_id'),
        'scope': config.get(provider).get('scopes'),
        'redirect_uri': config.get('redirect_uri'),
        'response_type': 'code',

    }
    return config.get(provider).get('auth_url') + '?' + urllib.urlencode(params)


def main():
    global config
    global provider

    if not path.isfile('config.json'):
        print("You must have a valid config.json to run this script. Read the README!")

    config = json.load(open('config.json'))

    server = AsyncServer()
    server.daemon = True
    server.start()

    webbrowser.open_new(auth_url())

    while True:
        time.sleep(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-p', '--provider', default='uber', help='The OAuth provider you are authenticating with.')

    args = parser.parse_args()
    global provider
    provider = args.provider

    main()
