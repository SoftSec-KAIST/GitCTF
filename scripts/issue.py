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

import json
import sys
from utils import iso8601_to_timestamp
from datetime import datetime, timedelta

def create_bug_label(github, query, label_name, color, desc):
    issue = {'name': label_name, 'descryption': desc, 'color': color}
    # Add the label to the repository
    if github.post(query, json.dumps(issue)) is None:
        print('[*] Label already exists in %s' % label_name)

def create_bug_labels(repo_owner, repo_name, github):
    '''Create an label on github.com'''
    query = '/repos/%s/%s/labels' % (repo_owner, repo_name)
    create_bug_label(github, query, 'intended', '9466CB',
                     'Exploit that triggers intended vulnerability.')
    create_bug_label(github, query, 'unintended', 'DA0019',
                     'Exploit that triggers unintended vulnerability.')

def update_bug_label(repo_owner, repo_name, issue_no, title, github):
    query = '/repos/%s/%s/issues/%s' % (repo_owner, repo_name, issue_no)
    labels = []
    if 'master' in title:
        labels.append('unintended')
    else:
        labels.append('intended')

    issue = {'labels': labels}
    r = github.patch(query, json.dumps(issue))
    if r is None:
        print '[*] Could not create comment in "%s/%s"' % (repo_name, issue_no)
    else:
        print '[*] Successfully created comment'


def make_github_issue(repo_owner, repo_name, title, body, github):
    '''Create an issue on github.com using the given parameters.'''
    query = '/repos/%s/%s/issues' % (repo_owner, repo_name)
    labels = []
    if 'master' in title:
        labels.append('unintended')
    else:
        labels.append('intended')

    issue = {'title': title, 'body': body, 'labels': labels}
    r = github.post(query, json.dumps(issue), 201)
    if r is None:
        print '[*] Could not create issue "%s"' % title
        print '[*] Response:', r
        sys.exit(-1)
    else:
        print '[*] Successfully created issue "%s"' % title

def get_github_issue(repo_owner, repo_name, issue_no, github):
    '''Retrieve an issue on github.com using the given parameters.'''
    query = '/repos/%s/%s/issues/%s' % (repo_owner, repo_name, issue_no)
    r = github.get(query)
    if r is None:
        print 'Could not get Issue from %s' % query
        print 'Response:', r
        sys.exit(-1)
    else:
        print '[*] Successfully obtained issue #%s' % issue_no
        print '[*] title:', r['title']
        print '[*] creater:', r['user']['login']
        dt = datetime.strptime(r['created_at'],'%Y-%m-%dT%H:%M:%SZ')
        # XXX do not assume it is in Korea, just use the current tz.
        open_time = dt + timedelta(hours = 9) # Change to the Korea time
        print '[*] open time:', open_time
        title = r['title']
        submitter = r['user']['login']
        create_time = r['created_at']
        content = r['body']
        create_timestamp = int(iso8601_to_timestamp(create_time))
        return (title, submitter, create_timestamp, content)

def submit_issue(title, encrypted_exploit, target_team, config, github):
    # Retrieve information from config
    repo_owner = config['repo_owner']
    repo_name = config['teams'][target_team]['repo_name']

    # Create issue label first
    create_bug_labels(repo_owner, repo_name, github)

    # Read in encrypted file content
    with open(encrypted_exploit, 'r') as f :
        content = f.read().rstrip()

    make_github_issue(repo_owner, repo_name, title, content, github)

def is_closed(repo_owner, repo_name, issue_no, github):
    query = '/repos/%s/%s/issues/%s' % (repo_owner, repo_name, issue_no)
    r = github.get(query)
    if r is None:
        print 'Could not get Issue from %s' % query
        print 'Response:', r
        return True     # Not deal with the error case. Just regard as closed
    else:
        if r['closed_at'] == None:
            return False
        else:
            return True

def create_comment(repo_owner, repo_name, issue_no, comment, github):
    query = '/repos/%s/%s/issues/%s/comments' % \
            (repo_owner, repo_name, issue_no)

    issue = {'body': comment}
    r = github.post(query, json.dumps(issue), 201)
    if r is None:
        print '[*] Could not create comment in "%s/%s"' % (repo_name, issue_no)
        print r
    else:
        print '[*] Successfully created comment'

def close_issue(repo_owner, repo_name, issue_no, github):
    query = '/repos/%s/%s/issues/%s' % \
            (repo_owner, repo_name, issue_no)

    issue = {'state': 'closed'}
    r = github.patch(query, json.dumps(issue))
    if r is None:
        print '[*] Could not close "%s/%s"' % (repo_name, issue_no)
    else:
        print '[*] Successfully closed'


# TODO : maybe we can add main function so this can be used like
# "python issue.py SUBMIT ..." or "python issue.py FETCH ..."
