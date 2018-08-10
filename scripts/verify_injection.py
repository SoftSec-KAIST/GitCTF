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
from utils import rmdir, load_config
from git import list_branches, clone, checkout
from verify_exploit import verify_exploit
from crypto import decrypt_exploit

def get_exploit_dir(dir, branch, config, team):
    # XXX current assumption: "exploit_bugN.zip.pgp"
    exploit_path = "exploit_%s.zip.pgp" % branch
    encrypted_exploit = os.path.join(dir, exploit_path)
    exploit_dir = decrypt_exploit(encrypted_exploit, config, team)
    if exploit_dir is None:
        print '[*] Failed to get decrypted exploit'
        sys.exit()
    return exploit_dir

def verify_injection(team, config_file):
    config = load_config(config_file)
    timeout = config["exploit_timeout"]["injection_phase"]
    repo_owner = config['repo_owner']
    repo_name = config['teams'][team]['repo_name']
    clone(repo_owner, repo_name)
    branches = list_branches(repo_name)
    branches.remove("master") # master branch is not verification target

    for branch in branches:
        checkout(repo_name, branch)
        exploit_dir = get_exploit_dir(repo_name, branch, config, team)
        bug_branch_result, _ = \
            verify_exploit(exploit_dir, repo_name, branch, timeout, config)

        checkout(repo_name, "master")
        master_result, _ = \
            verify_exploit(exploit_dir, repo_name, "master", timeout, config)

        rmdir(exploit_dir)

        if master_result == False and bug_branch_result == True:
            print '[*] Successflly verified branch "%s".' % branch
        elif bug_branch_result == True :
            print ('[*] Exploit for branch "%s" works, but it also works on ' \
                   'master branch, which indicates some error.' %  branch)
            sys.exit()
        else :
            print '[*] Failed to verify exploit in branch "%s".' %  branch
            sys.exit()

    rmdir(repo_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'Usage: ', sys.argv[0], '[team] [config file]'
        sys.exit()
    team = sys.argv[1]
    config_file = sys.argv[2]
    verify_injection(team, config_file)

