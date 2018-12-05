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
import os
from utils import load_config, rmfile, mkdir, random_string, rmdir
from utils import prompt_checkout_warning, print_and_log
from git import list_branches, clone, checkout
from git import get_latest_commit_hash
from issue import get_github_issue
from crypto import decrypt_exploit
from verify_exploit import verify_exploit
from github import Github
from datetime import datetime
from cmd import run_command

def verify_issue(defender, repo_name, issue_no, config, github, target_commit=None):
    timeout = config["exploit_timeout"]["exercise_phase"]
    repo_owner = config['repo_owner']
    title, submitter, create_time, content = \
        get_github_issue(repo_owner, repo_name, issue_no, github)

    # Issue convention: "exploit-[branch_name]"
    target_branch = title[8:]

    clone(repo_owner, repo_name)

    # Write the fetched issue content to temp file
    tmpfile = "/tmp/gitctf_%s.issue" % random_string(6)
    tmpdir = "/tmp/gitctf_%s.dir" % random_string(6)

    with open(tmpfile, "w") as f:
        f.write(content)

    # Decrypt the exploit
    mkdir(tmpdir)

    team = defender
    decrypt_exploit(tmpfile, config, team, tmpdir, submitter)
    rmfile(tmpfile)

    # Now iterate through branches and verify exploit
    branches = list_branches(repo_name)

    candidates = []
    if (target_branch in branches) and (target_commit is None):
        # Iterate through branches and collect candidates
        commit = get_latest_commit_hash(repo_name, create_time, target_branch)
        candidates.append((target_branch, commit))

    verified_branch = None
    verified_commit = None

    log = 'About %s (exploit-service branch)\n' % title

    for (branch, commit) in candidates:
        if branch in title:
            result, log = verify_exploit(tmpdir, repo_name, commit, timeout, \
                    config, log=log)
        else:
            result, _ = verify_exploit(tmpdir, repo_name, commit, timeout, \
                    config)

        if result:
            verified_branch = branch
            verified_commit = commit
            break

    rmdir(tmpdir)
    rmdir(repo_name)

    if verified_branch is None:
        print("[*] The exploit did not work against branch '%s'" % \
                target_branch)
    else:
        print("[*] The exploit has been verified against branch '%s'" %
              verified_branch)

    return (verified_branch, verified_commit, submitter, log)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: %s [repo name] [issue no] [config]" %
              sys.argv[0])
        sys.exit()
    repo_name = sys.argv[1]
    issue_no = sys.argv[2]
    config_file = sys.argv[3]
    config = load_config(config_file)
    github = Github(config["player"], None)
    verify_issue(repo_name, issue_no, config, github)
