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
from utils import base_dir, docker_cleanup
from cmd import run_command

def exec_service(name, service_dir, host_port, service_port):
    docker_cleanup(name)
    script = os.path.join(base_dir(), "setup_service.sh")
    host_port = int(host_port)
    service_port = int(service_port)
    _, err, e = run_command('%s "%s" %d %d' % \
                          (script, name, host_port, service_port), service_dir)
    if e != 0:
        print err
        print '[*] Failed to execute the service.'
    else:
        print '[*] Service is up.'

def exec_exploit(name, exploit_dir, ip, port, timeout):
    docker_cleanup(name)
    script = os.path.join(base_dir(), "launch_exploit.sh")
    _, err, e = run_command('%s "%s" %s %d %d' % \
                          (script, name, ip, port, \
                          timeout), exploit_dir)
    if e != 0:
        print err
        print '[*] Failed to execute the service.'
    else:
        print '[*] Service is up.'
