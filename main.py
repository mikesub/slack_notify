#!/usr/bin/env python3
import sys
import utils
import github
import jira

try:
    debug_mode = (sys.argv[1] != 'SLACK')
except IndexError:
    debug_mode = True

try:
    utils.send_to_slack(github.get_prs(), jira.get_issues(), debug_mode=debug_mode)
except Exception as any_error:
    utils.handle_error(any_error, debug_mode=debug_mode)
    sys.exit(1)
