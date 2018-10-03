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
import os
import shutil
import string
import json
import re
import time
import calendar
import dateutil.parser
import dateutil.tz
from random import *
from cmd import run_command

def print_and_log(msg, log=None):
    print msg
    if log != None:
        log = log + msg + '\n'
    return log

# Return alphanumeric random string of given length
def random_string(length):
    allchar = string.ascii_letters + string.digits
    rand_str = "".join(choice(allchar) for x in range(length))
    return rand_str

# Remove trailing slash from given path. This is sometimes needed when the given
# path is a directory path, where an unwanted trailing slash is appended by auto
# completion.
def remove_trailing_slash(path):
    while len(path) > 0 and path[-1] == "/":
      path = path[:-1]
    return path

def get_dirname(path):
    # First remove trailing slash
    path = remove_trailing_slash(path)
    idx = path.rfind("/")
    if idx == -1:
        return path
    else:
        return path[idx + 1:]

def copy(src_path, dst_path):
    try: shutil.copy2(src_path, dst_path)
    except: pass

# Same as `rm -rf`
def rmdir(dir):
    try: shutil.rmtree(dir)
    except: pass

# Same as rm -f
def rmfile(file):
    try: os.remove(file)
    except: pass

# Same as mkdir
def mkdir(dir):
    try: os.makedirs(dir)
    except: pass

# Return the base directory where all the scripts live in.
def base_dir():
    return os.path.dirname(os.path.realpath(__file__))

# Kill and remove the specified docker container
def docker_cleanup(container_name):
    print "[*] Clean up container '%s'" % container_name
    script = os.path.join(base_dir(), "cleanup.sh")
    cmdline = "%s %s" % (script, container_name)
    run_command(cmdline, None)

def load_config(config_file):
    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception as e:
        print "Cannot load configuration file %s" % config_file
        print repr(e)
        sys.exit(0)

def prompt_warning(msg):
    print msg
    print "Do you want to continue?",
    while True:
        ans = raw_input("(y/n):")
        if ans.lower() == "y":
            break
        elif ans.lower() == "n":
            print "[*] Script aborts."
            sys.exit()
        else:
            print "[*] Invalid input.",
            continue

def prompt_rmdir_warning(dir):
    if os.path.isdir(dir):
        warning_msg = "Directory %s already exists. " % dir
        warning_msg += "We will remove this directory and create new directory."
        prompt_warning(warning_msg)

def prompt_checkout_warning(dir):
    if os.path.isdir(dir):
        warning_msg = "We will forcefully checkout branch from %s. " % dir
        warning_msg += "You will lose ongoing works which are not commited yet."
        prompt_warning(warning_msg)

def iso8601_to_timestamp(str):
    dt = dateutil.parser.parse(str)
    return calendar.timegm(dt.astimezone(dateutil.tz.tzutc()).timetuple())

def is_timeover(config):
    current_time = int(time.time())
    end_time = int(iso8601_to_timestamp(config['end_time']))
    return current_time > end_time
