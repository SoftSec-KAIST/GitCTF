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
import os
from utils import load_config, prompt_rmdir_warning, rmdir, mkdir, base_dir
from github import Github
from cmd import run_command

def create_remote_repo(repo_owner, repo_name, github, description = None):
    query = '/orgs/%s/repos' % (repo_owner)

    repo = {'name': repo_name, 'description': description}
    r = github.post(query, json.dumps(repo), 201)

    print '[*] Creating %s remote repository' % (repo_name)
    if r is None:
        print '[*] Failed to create remote repository "%s".' % repo_name
        print '[*] Response:', r
        return False
    else:
        print '[*] Successfully created remote repository "%s".' % repo_name
        return True

def init_repo(dir_path):
    _, _, r = run_command('git init', dir_path)
    if r != 0:
        print '[*] Failed to git init'
        return False
    _, _, r = run_command('git remote add origin git@github.com:%s.git' % \
            (dir_path), dir_path)
    if r != 0:
        print '[*] Failed to git remote add origin %s.' % (dir_path)
        return False
    return True

def create_local_repo(dir_path):
    print '[*] Creating %s local repositoy.' % (dir_path)
    mkdir(dir_path)
    return init_repo(dir_path)

def commit_and_push(path, msg):
    _, _, r = run_command('git add -A .', path)
    if r != 0:
        print('[*] Failed to git add -A . in %s.' % path)
        return False
    _, _, r = run_command('git commit -m "%s"' % (msg), path)
    if r != 0:
        print('[*] Failed to commit in %s.' % path)
        return False
    _, _, r = run_command('git push -u origin master', path)
    if r != 0:
        print('[*] Failed to push in %s.' % path)
        return False
    return True

def local_setup(repo_owner, scoreboard_name, problems):
    print '[*] Start local setup'
    # Create root directory for CTF env.
    prompt_rmdir_warning(repo_owner)
    rmdir(repo_owner)
    mkdir(repo_owner)

    # Setup local scoreboard repo
    scoreboard_dir_path = os.path.join(repo_owner, scoreboard_name)
    if create_local_repo(scoreboard_dir_path):
        open(os.path.join(scoreboard_dir_path, 'score.csv'), 'a').close()

    # Setup local problems repo
    for problem in problems:
        problem_dir_path = os.path.join(repo_owner, \
                problems[problem]['repo_name'])
        if create_local_repo(problem_dir_path):
            # XXX: add following algorithm
            # 1. Copy binary
            # 2. Make Dockerfile
            pass

# About scoreboard and each problem:
# 1. Create remote repositoy
# 2. Commit and push
def remote_setup(repo_owner, scoreboard_name, problems, github):
    print '[*] Start remote setup'
    # Setup remote scoreboard repo
    result = create_remote_repo(repo_owner, scoreboard_name, github, \
            'Scoreboard')
    if result:
        scoreboard_dir_path = os.path.join(repo_owner, scoreboard_name)
        commit_and_push(scoreboard_dir_path, 'Initialize scoreboard')

    # Setup remote problems repo
    for problem in problems:
        prob_repo_name = problems[problem]['repo_name']
        description = problems[problem]['description']
        result = create_remote_repo(repo_owner, prob_repo_name, github, \
                description)
        if result:
            problem_dir_path = os.path.join(repo_owner, \
                    problems[problem]['repo_name'])
            commit_and_push(problem_dir_path, 'Add problem: %s' % \
                    prob_repo_name)

def setup_env(admin_config_file, token=None):
    admin_config = load_config(admin_config_file)
    repo_owner = admin_config['repo_owner']
    scoreboard_name = admin_config['scoreboard_name']
    problems = admin_config['problems']

    local_setup(repo_owner, scoreboard_name, problems)

    github = Github(admin_config['instructor'], token)

    remote_setup(repo_owner, scoreboard_name, problems, github)
