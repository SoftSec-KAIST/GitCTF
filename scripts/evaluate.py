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
import re
import sys
import csv
import json
import time
import calendar
from issue import is_closed, create_comment, close_issue
from issue import create_bug_labels, update_bug_label, get_github_issue
from cmd import run_command
from utils import load_config, rmdir, rmfile, iso8601_to_timestamp, is_timeover
from github import Github, get_github_path
from git import clone, checkout, get_next_commit_hash
from verify_issue import verify_issue

msg_file = 'msg' # Temporarily store commit message

def failure_action(repo_owner, repo_name, issue_no, comment, id, github):
    print comment
    create_comment(repo_owner, repo_name, issue_no, comment, github)
    close_issue(repo_owner, repo_name, issue_no, github)
    mark_as_read(id, github)

def get_target_repos(config):
    repos = []
    for team in config['teams']:
        repos.append(config['teams'][team]['repo_name'])
    return repos

def is_issue(noti):
    return noti['subject']['type'] == 'Issue'

def is_target(noti, target_repos):
    return noti['repository']['name'] in target_repos

def get_issue_number(noti):
    return int(noti['subject']['url'].split('/')[-1])

def get_issue_id(noti):
    return noti['url'].split('/')[-1]

def get_issue_gen_time(noti):
    return iso8601_to_timestamp(noti['updated_at'])

def get_issues(target_repos, github):
    issues = []
    query = '/notifications'
    try:
        notifications, interval = github.poll(query)
    except ConnectionError:
        return [], 60
    for noti in reversed(notifications):
        if noti['unread'] and is_issue(noti) and is_target(noti, target_repos):
            num = get_issue_number(noti)
            id = get_issue_id(noti)
            gen_time = get_issue_gen_time(noti)
            issues.append((noti['repository']['name'], num, id, gen_time))
    return issues, interval

def mark_as_read(issue_id, github):
    query = '/notifications/threads/' + issue_id
    return github.patch(query, None)

def get_defender(config, target_repo):
    teams = config['teams']
    defender = None
    for team in teams:
        if teams[team]['repo_name'] == target_repo:
            defender = team
            break
    return defender

def sync_scoreboard(scoreboard_dir):
    run_command('git reset --hard', scoreboard_dir)
    run_command('git pull', scoreboard_dir)

def point_hash(attacker, defender, bugkind):
    return (attacker + '_' + defender + '_' + bugkind)

def is_dup(scoreboard_dir, h): # XXX slow
    with open(os.path.join(scoreboard_dir, 'score.csv')) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if len(row) == 0:
                return False
            if point_hash(row[1], row[2], row[3]) == h:
                return True
        return False

def write_score(stamp, info, scoreboard_dir, pts):
    with open(os.path.join(scoreboard_dir, 'score.csv'), 'a') as f:
        attacker = info['attacker']
        defender = info['defender']
        kind = info['bugkind']
        f.write('%s,%s,%s,%s,%d\n' % (stamp, attacker, defender, kind, pts))

def write_message(info, scoreboard_dir, pts):
    with open(os.path.join(scoreboard_dir, msg_file), 'w') as f:
        attacker = info['attacker']
        defender = info['defender']
        kind = info['bugkind']
        f.write('[Score] %s +%d\n\n' % (attacker, pts))
        if kind.startswith('bug'):
            f.write('%s attacked `%s` of %s' % (attacker, kind, defender))
        elif pts == 0: # Protocol to indicate successfull defense
            f.write('%s defended %s with %s' % (defender, attacker, kind))
        else:
            f.write('%s attacked %s of %s' % (attacker, kind, defender))

def commit_and_push(scoreboard_dir):
    _, _, r = run_command('git add score.csv', scoreboard_dir)
    if r != 0:
        print('[*] Failed to git add score.csv.')
        return False
    _, _, r = run_command('git commit -F %s' % msg_file, scoreboard_dir)
    if r != 0:
        print('[*] Failed to commit score.csv.')
        return False
    _, _, r = run_command('git push origin master', scoreboard_dir)
    if r != 0:
        print('[*] Failed to push the score.')
        return False
    rmfile(os.path.join(scoreboard_dir, msg_file))
    return True

def find_the_last_attack(scoreboard_dir, timestamp, info):
    last_commit = None
    with open(os.path.join(scoreboard_dir, 'score.csv')) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if int(row[0]) >= timestamp and len(row[3]) == 40:
                if row[1] == info['attacker'] and row[2] == info['defender']:
                    last_commit = row[3]
    return last_commit

def get_next_commit(last_commit, defender, config):
    repo_name = config['teams'][defender]['repo_name']
    rmdir(repo_name)
    clone(config['repo_owner'], repo_name)
    next_commit_hash = get_next_commit_hash(repo_name, 'master', last_commit)
    rmdir(repo_name)
    print next_commit_hash
    if next_commit_hash == '':
        return None
    else:
        return next_commit_hash

# XXX: Calling verify_issue() multiple times involves redundant process
# internally. We may consider replacing this by calling fetch() once and then
# calling verify_exploit() multiple times.
def process_unintended(repo_name, num, config, gen_time, info, scoreboard, id,
                        github):
    unintended_pts = config['unintended_pts']
    target_commit = find_the_last_attack(scoreboard, gen_time, info)
    if target_commit is None:
        # This exploit is previously unseen, give point.
        write_score(gen_time, info, scoreboard, unintended_pts)
        write_message(info, scoreboard, unintended_pts)
        commit_and_push(scoreboard)
    else:
        while True:
            target_commit = get_next_commit(target_commit, \
                    info['defender'], config)
            if target_commit is None:
                print '[*] No more commit to verify against'
                break

            _, verified_commit, _, _ = \
                verify_issue(info['defender'], repo_name, num, config, \
                github, target_commit)
            info['bugkind'] = target_commit
            if verified_commit is None:
                # Found a correct patch that defeats the exploit.
                current_time = int(time.time())
                write_score(current_time, info, scoreboard, 0)
                write_message(info, scoreboard, 0)
                commit_and_push(scoreboard)
                mark_as_read(id, github)
                break
            else:
                # Exploit still works on this commit, update score and continue
                write_score(gen_time, info, scoreboard, unintended_pts)
                write_message(info, scoreboard, unintended_pts)
                commit_and_push(scoreboard)

def process_intended(repo_name, num, config, time, info, scoreboard, id, github):
    intended_pts = config['intended_pts']
    hash = point_hash(info['attacker'], info['defender'], info['bugkind'])
    if is_dup(scoreboard, hash):
        failure_action(config['repo_owner'], repo_name, num, \
                '[*] Duplicate bug.', id, github)
        return
    write_score(time, info, scoreboard, intended_pts)
    write_message(info, scoreboard, intended_pts)
    if commit_and_push(scoreboard):
        mark_as_read(id, github)

def process_issue(repo_name, num, id, config, gen_time, github, scoreboard):
    repo_owner = config['repo_owner']
    if is_closed(repo_owner, repo_name, num, github):
        mark_as_read(id, github)
        return

    create_bug_labels(repo_owner, repo_name, github)
    title, _, _, _ = get_github_issue(repo_owner, repo_name, num, github)
    update_bug_label(repo_owner, repo_name, num, title, github)

    defender = get_defender(config, repo_name)
    if defender is None:
        print '[*] Fatal error: unknown target %s.' % repo_name
        sys.exit()
        return

    branch, commit, attacker, log = verify_issue(defender, repo_name, num, \
            config, github)
    if branch is None:
        log = "```\n" + log + "```"
        failure_action(repo_owner, repo_name, num, \
                log + '\n\n[*] The exploit did not work.', id, github)
        return

    if config['individual'][attacker]['team'] == defender:
        failure_action(repo_owner, repo_name, num, \
                '[*] Self-attack is not allowed: %s.' % attacker, \
                id, github)
        return

    if branch == "master":
        kind = commit
    else:
        kind = branch
    info = {'attacker': attacker, 'defender': defender, 'bugkind': kind}
    sync_scoreboard(scoreboard)
    if kind.startswith('bug'):
        process_intended(repo_name, num, config, gen_time, info, scoreboard, \
                id, github)
    else:
        process_unintended(repo_name, num, config, gen_time, info, scoreboard,
                            id, github)

def prepare_scoreboard_repo(url):
    path = get_github_path(url).split('/')
    scoreboard_owner = path[0]
    scoreboard_name = path[1]
    scoreboard_dir = '.score'
    clone(scoreboard_owner, scoreboard_name, False, scoreboard_dir)
    return scoreboard_dir

def start_eval(config, github):
    target_repos = get_target_repos(config)
    scoreboard = prepare_scoreboard_repo(config['score_board'])
    finalize = False
    while (not finalize):
        if (is_timeover(config)):
            finalize = True
        issues, interval = get_issues(target_repos, github)
        if not issues:
            print('[*] No news. Sleep for %d seconds.' % interval)
            time.sleep(interval)
            continue
        print('[*] %d new issues.' % len(issues))
        for repo, num, id, gen_time in issues:
            process_issue(repo, num, id, config, gen_time, github, scoreboard)
    print '[*] Time is over!'
    return

def evaluate(config_file, token):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    config = load_config(config_file)
    github = Github(config['player'], token)
    return start_eval(config, github)

