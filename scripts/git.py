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
from cmd import run_command
from utils import base_dir, prompt_rmdir_warning, rmdir

def list_branches(dir):
    external_path = os.path.join(base_dir(), "list_branches.sh")
    s, _, _ = run_command("%s \"%s\"" % (external_path, dir), os.getcwd())
    branches = s.splitlines()
    return branches

def clone(repo_owner, repo_name, prompt=False, target_dir=None):
    target = repo_name if target_dir is None else target_dir
    if prompt:
        prompt_rmdir_warning(target)
    rmdir(target)
    url = 'git@github.com:%s/%s' % (repo_owner, repo_name)
    _, err, r = run_command("git clone %s %s" % (url, target), os.getcwd())
    if r!= 0:
        print '[*] Failed to clone: "%s"' % url
        print err
        sys.exit()

def checkout(dir, br):
    _, err, r = run_command("git -C %s checkout -f %s" % (dir, br), os.getcwd())
    if r != 0:
        print("[*] Failed to checkout the branch %s" % br)
        print err
        sys.exit()

def get_latest_commit_hash(dir, create_time, branch='master'):
    command = 'git -C %s rev-list --max-count=1 --before=%d %s' \
                    % (dir, create_time, branch)
    output, err, r = run_command(command, os.getcwd())
    if r != 0:
        print("[*] Failed to get the latest commit before %s" % create_time)
        print err
        sys.exit()
    return output.strip()

def get_next_commit_hash(dir, branch, commit_hash):
    command = 'git -C %s rev-list --reverse --ancestry-path %s..origin/%s' \
            % (dir, commit_hash, branch)
    output, err, r = run_command(command, os.getcwd())
    if r != 0:
        print("[*] Failed to get the next commit after %s" % commit_hash)
        print err
        sys.exit()
    output = output.split('\n')[0]
    return output.strip()
