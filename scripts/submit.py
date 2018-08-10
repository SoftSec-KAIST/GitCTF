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
from git import list_branches
from verify_exploit import verify_exploit
from crypto import encrypt_exploit
from issue import submit_issue
from utils import rmfile, load_config, prompt_checkout_warning
from github import Github

def submit(exploit_dir, service_dir, target, config_file, token=None):
    config = load_config(config_file)
    timeout = config["exploit_timeout"]["exercise_phase"]
    prompt_checkout_warning(service_dir)
    branches = list_branches(service_dir)

    verified_branch = None
    for branch in branches:
        result, _ = verify_exploit(exploit_dir, service_dir, branch, timeout, config)
        if result:
            verified_branch = branch
            break

    if verified_branch is None :
        print("[*] Your exploit did not work against any of the branch")
        sys.exit()

    print("[*] Your exploit has been verified against branch '%s'"
            % verified_branch)

    # Not encrypt exploit
    signer = config["player"]
    encrypted_exploit = encrypt_exploit(exploit_dir, target, config, signer)
    if encrypted_exploit is None:
        print "[*] Failed to encrypt exploit"
        sys.exit(0)

    # Submit an issue with the encrypted exploit
    issue_title = "exploit-%s" % verified_branch
    github = Github(config["player"], token)
    submit_issue(issue_title, encrypted_exploit, target, config, github)

    # Clean up
    rmfile(encrypted_exploit)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: %s [exploit dir] [service dir] [target team] [config]" %
              sys.argv[0])
        sys.exit()
    exploit_dir = sys.argv[1]
    service_dir = sys.argv[2]
    target = sys.argv[3]
    config = sys.argv[4]
    submit(exploit_dir, service_dir, target, config)
