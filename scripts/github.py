#!/usr/bin/env python
###############################################################################
# Git-based CTF
###############################################################################
#
# Author: SeongIl Wi <seongil.wi@kaist.ac.kr>
#         Jaeseung Choi <jschoi17@kaist.ac.kr>
#         Sang Kil Cha <sangkilc@kaist.ac.kr>
#
# Copyright (c) 2018 SoftSec Lab. KAIST
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
import json
import requests
import getpass
import base64

def decode_content(response):
    if response['encoding'] == 'base64':
        return base64.b64decode(response['content'])
    else:
        print('[*] Unknown encoding %s' % response['encoding'])
        sys.exit()

def trim_dot_git(repo_name):
    if repo_name.endswith('.git'):
        return repo_name[:-4]
    else:
        return repo_name

def get_github_path(url):
    if url.startswith('https://github.com/'):
        grp = url[19:].split('/')
    elif url.startswith('git@github.com:'):
        grp = url[15:].split('/')
    else:
        print("[*] Failed to obtain github path")
        sys.exit()
    owner = grp[0]
    repo_name = trim_dot_git(grp[1])
    return (owner + '/' + repo_name) # We just call this `GitHub path`

def result(r, expected_code):
    if r.status_code == expected_code:
        return json.loads(r.content)
    else:
        return None

class Github():
    def __init__(self, username, token=None):
        self.session = requests.Session()
        if token is None:
            print 'Github ID: %s' % username
            password = getpass.getpass('Password: ')
            self.session.auth = (username, password)
        else:
            self.session.headers['Authorization'] = 'token %s' % token

    @property
    def url(self):
        return 'https://api.github.com'

    def post(self, query, data, expected_code=201):
        return result(self.session.post(self.url + query, data), expected_code)

    def get(self, query, expected_code=200):
        return result(self.session.get(self.url + query), expected_code)

    def put(self, query, data):
        r = self.session.put(self.url + query, data = data)
        return r.status_code == 205

    def patch(self, query, data):
        r = self.session.patch(self.url + query, data = data)
        return r.status_code == 205

    def poll(self, query):
        r = self.session.get(self.url + query)
        poll_interval = int(r.headers['X-Poll-Interval'])
        response = result(r, 200)
        return response, poll_interval
