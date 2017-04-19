#!/usr/bin/env python3
import sys
import utils
import github
import jira

try:
    utils.send_to_slack(github.get_prs(), jira.get_issues())
except Exception as any_error:
    utils.handle_error(any_error)
    sys.exit(1)
