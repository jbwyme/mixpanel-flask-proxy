
from flask import Flask, Response, request
from flask_cors import cross_origin
import requests
import sys

def filter_headers(headers):
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'access-control-allow-credentials', 'access-control-allow-origin']
    return [(name, value) for (name, value) in headers
            if name.lower() not in excluded_headers]

def create_app():
    app = Flask(__name__)

    @app.route('/lib.js')
    def js_lib():
        resp = requests.get('https://cdn.mxpnl.com/libs/mixpanel-2-latest.js')
        headers = filter_headers(resp.raw.headers.items())
        return Response(resp.content, resp.status_code, headers)

    @app.route('/lib.min.js')
    def js_lib_minified():
        resp = requests.get('https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js')
        headers = filter_headers(resp.raw.headers.items())
        return Response(resp.content, resp.status_code, headers)

    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
    @app.route('/<path:path>', methods=['GET', 'POST'])
    @cross_origin(supports_credentials=True, send_wildcard=False)
    def root(path):

        # This relays the client's IP for geolocation lookup
        # The method via which you can retrieve the "real" client IP
        # is implementation specific so you may need to change this logic.
        if 'HTTP_X_FORWARDED_FOR' in request.environ:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        elif 'HTTP_X_REAL_IP' in request.environ:
            ip = request.environ['HTTP_X_REAL_IP']
        else:
            ip = request.remote_addr

        headers = {'X-REAL-IP': ip}

        resp = requests.request(
            method=request.method,
            url='https://api.mixpanel.com%s' % request.path,
            headers=headers,
            params=request.args,
            data=request.form,
        )
        headers = filter_headers(resp.raw.headers.items())
        return Response(resp.content, resp.status_code, headers)

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0')
