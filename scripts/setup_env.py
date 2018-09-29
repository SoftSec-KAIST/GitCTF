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
from utils import load_config
from github import Github


def create_repository(repo_owner, repo_name, github, description = None):
    query = "/orgs/%s/repos" % (repo_owner)

    repo = {"name": repo_name, "description": description}
    r = github.post(query, json.dumps(repo), 201)

    if r is None:
        print '[*] Failed to create repository "%s"' % repo_name
        print '[*] Response:', r
    else:
        print '[*] Successfully created repository "%s"' % repo_name

def setup_env(admin_config_file, token=None):
    admin_config = load_config(admin_config_file)
    repo_owner = admin_config['repo_owner']
    scoreboard_name = admin_config['scoreboard_name']

    github = Github(admin_config["instructor"], token)

    # Create scoreboard repo
    print "[*] Creating scoreboard repository"
    create_repository(repo_owner, scoreboard_name, github, "Scoreboard")
    print

    # Create problems repo
    problems = admin_config['problems']
    for problem in problems:
        prob_repo_name = problems[problem]["repo_name"]
        description = problems[problem]["description"]
        print "[*] Creating %s repository" % prob_repo_name
        create_repository(repo_owner, prob_repo_name, github, description)
