"""
Make calls to the nanoHUB web API

Benjamin P. Haley, Purdue University (bhaley@purdue.edu)

Copyright 2017 HUBzero Foundation, LLC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

HUBzero is a registered trademark of Purdue University.
"""

from urllib import urlencode
from urllib2 import urlopen, Request, HTTPError
import sys, json, time

url = r'https://nanohub.org/api'
sleep_time = 1.5

def do_get(url, path, data, hdrs):
    """Send a GET to url/path; return JSON output"""
    d = urlencode(data)
    r = Request('{0}/{1}?{2}'.format(url, path, d) , data=None, headers=hdrs)
    try:
        u = urlopen(r)
    except HTTPError as e:
        msg = 'GET {0} failed ({1}): {2}\n'.format(r.get_full_url(), \
                                                   e.code, \
                                                   e.reason)
        sys.stderr.write(msg)
        sys.exit(1)
    return json.loads(u.read())

def do_post(url, path, data, hdrs):
    """Send a POST to url/path; return JSON output"""
    d = urlencode(data)
    r = Request('{0}/{1}'.format(url, path) , data=d, headers=hdrs)
    try:
        u = urlopen(r)
    except HTTPError as e:
        msg = 'POST {0} failed ({1}): {2}\n'.format(r.get_full_url(), \
                                                    e.code, \
                                                    e.reason)
        sys.stderr.write(msg)
        sys.exit(1)
    return json.loads(u.read())

def authenticate(auth_data):
    """Get authentication token; return authorization headers"""
    auth_json = do_post(url, 'developer/oauth/token', auth_data, hdrs={})
    return {'Authorization': 'Bearer {}'.format(auth_json['access_token'])}

def launch_tool(driver_json, headers):
    """Start a tool session; return the session id"""
    run_json = do_post(url, 'tools/run', driver_json, headers)
    return run_json['session']

def get_results(session_id, headers):
    """Wait for the tool session to finish; return the run XML"""
    status_data = {'session_num': session_id}
    while True:
        time.sleep(sleep_time)
        status_json = do_get(url, 'tools/status', status_data, headers)
        if status_json['finished'] is True:
            break
    time.sleep(sleep_time)  # let the DB update
    result_data = {
        'session_num': session_id,
        'run_file': status_json['run_file']
    }
    result_json = do_get(url, 'tools/output', result_data, headers)
    return result_json['output']

