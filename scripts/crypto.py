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
import json
import subprocess
import re
import shutil
import zipfile
from utils import random_string, rmdir, rmfile, remove_trailing_slash
from cmd import run_command

def decrypt_exploit(encrypted_exploit_path, config, team, out_dir=None, \
        expected_signer=None):
    if out_dir is None:
        out_dir = "exploit"

    rmdir(out_dir)

    tmpzip = "/tmp/gitctf_%s.zip" % random_string(6)
    tmpdir = "/tmp/gitctf_%s" % random_string(6)
    tmpgpg = "/tmp/gitctf_%s.gpg" % random_string (6)

    if expected_signer == None:
        decrypt_cmd = 'gpg -o %s %s' % (tmpzip, encrypted_exploit_path)
    else:
        instructor_id = config['teams']['instructor']['pub_key_id']
        team_id = config['teams'][team]['pub_key_id']
        expected_signer_id = config['individual'][expected_signer]['pub_key_id']

        # Make keyring
        run_command("gpg -o %s --export %s %s %s" % (tmpgpg, \
                expected_signer_id, instructor_id, team_id), os.getcwd())

        decrypt_cmd = "gpg --no-default-keyring --keyring %s -o %s %s" \
                % (tmpgpg, tmpzip, encrypted_exploit_path)

    _, err, r = run_command(decrypt_cmd, os.getcwd())
    if r != 0:
        print "[*] Failed to decrypt/verify %s" % encrypted_exploit_path
        print err
        return None

    run_command('unzip %s -d %s' % (tmpzip, tmpdir), os.getcwd())
    shutil.move(tmpdir, out_dir)

    rmfile(tmpzip)
    rmfile(tmpgpg)
    rmdir(tmpdir)

    return out_dir

def encrypt_exploit(exploit_dir, target_team, config, signer=None):
    # Remove trailing slash, for user convenience
    exploit_dir = remove_trailing_slash(exploit_dir)
    out_file = exploit_dir + ".zip.pgp"

    # Retrieve information from config
    teams = config["teams"]
    instructor_pubkey = teams["instructor"]["pub_key_id"]
    target_pubkey = teams[target_team]['pub_key_id']

    # Zip the directory
    tmp_path = "/tmp/gitctf_%s" % random_string(6)
    shutil.make_archive(tmp_path, "zip", exploit_dir)
    zip_file = tmp_path + ".zip" # make_archive() automatically appends suffix.

    # Encrypt the zipped file

    encrypt_cmd = "gpg -o %s " % out_file
    if signer is not None:
        signer_pubkey = config["individual"][signer]['pub_key_id']
        encrypt_cmd += "--default-key %s --sign " % signer_pubkey
    encrypt_cmd += "-e -r %s -r %s " % (instructor_pubkey, target_pubkey)
    encrypt_cmd += "--armor %s" % zip_file
    _, err, ret = run_command(encrypt_cmd, None)
    rmfile(zip_file) # Clean up zip file.
    if ret != 0:
        print "[*] Failed to sign/encrypt %s" % zip_file
        print err
        return None

    return out_file


# TODO : maybe we can add main function so this can be used like
# "python crypto.py ENCRYPT ..." or "python crypto.py DECRYPT ..."
