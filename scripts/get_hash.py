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

import os
import sys
import json
import time
from evaluate import get_target_repos
from utils import prompt_warning, load_config, rmdir
from git import clone, list_branches, checkout
from git import get_latest_commit_hash
from github import Github


def start_get_hash(config, github, config_file):
    repo_owner = config['repo_owner']
    for team in config['teams']:
        repo_name = config['teams'][team]['repo_name']
        if repo_name == '-':
            continue

        print('[*] Get the commit hash of %s repo.' % repo_name)
        clone(repo_owner, repo_name)
        branches = list_branches(repo_name)
        branches.remove("master") # Do not consider master branch
        for branch in branches:
            checkout(repo_name, branch)
            hash = get_latest_commit_hash(repo_name, int(time.time()), branch)
            config['teams'][team][branch] = hash
        rmdir(repo_name)

    with open(config_file, 'w') as outfile:
        json.dump(config, outfile, indent=4)

    print ('[*] Successfully write in %s' % config_file)

    return

def get_hash(config_file, token):
    prompt_warning('File %s will be changed.' % config_file)
    config = load_config(config_file)
    github = Github(config['player'], token)
    return start_get_hash(config, github, config_file)

