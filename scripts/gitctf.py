#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import argparse
from utils import prompt_checkout_warning, load_config
from execute import exec_service, exec_exploit
from submit import submit
from fetch import fetch
from verify_service import verify_service
from verify_exploit import verify_exploit
from verify_injection import verify_injection
from show_score import show_score
from evaluate import evaluate
from get_hash import get_hash
from setup_env import setup_env

def add_exploit(parser):
    parser.add_argument("--exploit", metavar="DIR", required=True,
                        help="specify the exploit directory")

def add_service_dir(parser):
    parser.add_argument("--service-dir", metavar="DIR", required=True,
                        help="specify the service directory")

def add_service_name(parser):
    parser.add_argument("--service-name", metavar="SRVNAME", required=True,
                        help="specify the name of the service")

def add_team(parser):
    parser.add_argument("--team", metavar="TEAM", required=True,
                        help="specify the team to verify")

def add_target(parser):
    parser.add_argument("--target", metavar="TEAM", required=True,
                        help="specify the target team")

def add_branch(parser):
    parser.add_argument("--branch", metavar="BRANCH", required=True,
                        help="specify the target branch")

def add_host_port(parser):
    parser.add_argument("--host-port", metavar="NUM", default="4000",
                        help="specify the host port number (default: 4000)")

def add_service_port(parser):
    parser.add_argument("--service-port", metavar="NUM", default="4000",
                        help="specify the service port number (default: 4000)")

def add_conf(parser):
    parser.add_argument("--conf", metavar="FILE", default="config.json",
                        help="specify the config file (default: config.json)")

def add_admin_conf(parser):
    parser.add_argument("--admin-conf", metavar="FILE", default=".config.json",
            help="specify the administrative config file (default: .config.json)")

def add_token(parser, required):
    parser.add_argument("--token", metavar="APITOKEN", required=required,
                        help="specify the GitHub API token")

def verify_service_main(prog, options):
    desc = 'verify service docker'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_team(parser)
    add_branch(parser)
    add_host_port(parser)
    add_service_port(parser)
    add_conf(parser)
    args = parser.parse_args(options)
    verify_service(args.team, args.branch, args.service_port, args.host_port,
                   args.conf)

def verify_exploit_main(prog, options):
    desc = 'verify written exploit'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_exploit(parser)
    add_service_dir(parser)
    add_branch(parser)
    add_conf(parser)
    parser.add_argument("--encrypt", dest="encrypt", action="store_true",
                        default=False,
                        help="specify whether to encrypt the verified exploit")
    parser.add_argument("--timeout", metavar="SEC", required=True,
                        help="specify timeout for exploit")
    args = parser.parse_args(options)
    prompt_checkout_warning(args.service_dir)
    config = load_config(args.conf)
    verify_exploit(args.exploit, args.service_dir, args.branch,
                   int(args.timeout), config, args.encrypt)

def verify_injection_main(prog, options):
    desc = 'verify injected vulnerabilities'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_team(parser)
    add_conf(parser)
    args = parser.parse_args(options)
    verify_injection(args.team, args.conf)

def submit_main(prog, options):
    desc = 'submit an exploit'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_exploit(parser)
    add_service_dir(parser)
    add_target(parser)
    add_token(parser, False)
    add_conf(parser)
    args = parser.parse_args(options)
    submit(args.exploit, args.service_dir, args.target, args.conf, args.token)

def fetch_main(prog, options):
    desc = 'fetch an exploit'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    parser.add_argument("--issue", metavar="NO", required=True,
                        help="specify the issue number")
    add_team(parser)
    add_conf(parser)
    add_token(parser, False)
    args = parser.parse_args(options)
    config = load_config(args.conf)
    fetch(args.team, args.issue, config, args.token)

def verify_main(prog, options):
    if len(options) == 0:
        print 'Usage:', prog, '<action> [options ...]\n'
        print 'Possible actions:'
        print '    service   : validate a service'
        print '    exploit   : validate an exploit'
        print '    injection : validate injected vulnerabilities'
        sys.exit()
    action = options[0]
    if action == 'service':
        verify_service_main(prog + ' service', options[1:])
    elif action == 'exploit':
        verify_exploit_main(prog + ' exploit', options[1:])
    elif action == 'injection':
        verify_injection_main(prog + ' injection', options[1:])
    else:
        print 'Unknown action.'

def score_main(prog, options):
    desc = 'show the current score'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_token(parser, False)
    add_conf(parser)
    args = parser.parse_args(options)
    show_score(args.token, args.conf)

def hash_main(prog, options):
    desc = 'get latest hash of commit for each branch'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_conf(parser)
    add_token(parser, False)
    args = parser.parse_args(options)
    get_hash(args.conf, args.token)

def setup_main(prog, options):
    desc = 'setup CTF environment'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_admin_conf(parser)
    add_token(parser, False)
    args = parser.parse_args(options)
    setup_env(args.admin_conf, args.token)

def eval_main(prog, options):
    desc = 'evaluate participants'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_conf(parser)
    add_token(parser, True)
    args = parser.parse_args(options)
    evaluate(args.conf, args.token)

def exec_service_main(prog, options):
    desc = 'execute a service'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    add_service_dir(parser)
    add_service_name(parser)
    add_host_port(parser)
    add_service_port(parser)
    args = parser.parse_args(options)
    exec_service(args.service_name,
                 args.service_dir,
                 args.host_port,
                 args.service_port)

def exec_exploit_main(prog, options):
    desc = 'execute an exploit'
    parser = argparse.ArgumentParser(description=desc, prog=prog)
    parser.add_argument("--exploit-dir", metavar="DIR", required=True,
                        help="specify the exploit directory")
    add_service_name(parser)
    parser.add_argument("--ip", metavar="ADDR", default="127.0.0.1",
                        help="specify the IP address (default: 127.0.0.1)")
    parser.add_argument("--port", metavar="NUM", default="4000",
                        help="specify the IP address (default: 4000)")
    parser.add_argument("--timeout", metavar="SEC", required=True,
                        help="specify timeout for exploit")
    args = parser.parse_args(options)
    exec_exploit(args.service_name, args.exploit_dir, args.ip, int(args.port), \
            int(args.timeout))

def exec_main(prog, options):
    if len(options) == 0:
        print 'Usage:', prog, '<target> [options ...]\n'
        print 'Possible targets:'
        print '    service   : execute a service'
        print '    exploit   : execute an exploit'
        sys.exit()
    target = options[0]
    if target == 'service':
        exec_service_main(prog + ' service', options[1:])
    elif target == 'exploit':
        exec_exploit_main(prog + ' exploit', options[1:])
    else:
        print 'Unknown action.'

def print_usage():
    print 'Usage:', sys.argv[0], '<action> [options ...]\n'
    print 'Possible actions:'
    print '    help      : show this help'
    print '    exec      : execute service/exploit'
    print '    verify    : verify service/injection/exploit'
    print '    submit    : submit an exploit'
    print '    fetch     : fetch an exploit'
    print '    score     : show the score'
    print '    hash      : get hash of each branch (for administrative purpose)'
    print '    eval      : manage the game score (for administrative purpose)'
    print '    setup     : setup the CTF env. (for administrative purpose)'
    sys.exit()

def print_logo():
        print (r"""
   ___ _ _        _                        _     ___  _____  ___
  / _ (_) |_     | |__   __ _ ___  ___  __| |   / __\/__   \/ __\
 / /_\/ | __|____| '_ \ / _` / __|/ _ \/ _` |  / /     / /\/ _\
/ /_\\| | ||_____| |_) | (_| \__ \  __/ (_| | / /___  / / / /
\____/|_|\__|    |_.__/ \__,_|___/\___|\__,_| \____/  \/  \/
  """)


def main(action, options):
    if action == 'help':
        print_usage()
    elif action == 'exec':
        exec_main(sys.argv[0] + ' exec', options)
    elif action == 'verify':
        verify_main(sys.argv[0] + ' verify', options)
    elif action == 'submit':
        submit_main(sys.argv[0] + ' submit', options)
    elif action == 'fetch':
        fetch_main(sys.argv[0] + ' fetch', options)
    elif action == 'score':
        score_main(sys.argv[0] + ' score', options)
    elif action == 'hash':
        hash_main(sys.argv[0] + ' hash', options)
    elif action == 'eval':
        eval_main(sys.argv[0] + ' eval', options)
    elif action == 'setup':
        setup_main(sys.argv[0] + ' setup', options)
    else:
        print 'Unknown action.'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_logo()
        print_usage()
    main(sys.argv[1], sys.argv[2:])
