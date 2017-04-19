DEBUG = True

gh_token = ''
gh_user_agent = ''
gh_search_url = 'https://api.github.com/search/issues?q=type:pr+is:open+user:ORGANIZATION'

slack_webhook_url = 'https://hooks.slack.com/services/{etc}'
slack_debug_channel = 'YOUR_SLACK_USERNAME'

gh_slack_mapping = {
    'github_name': 'slack_name',
}

jira_slack_mapping = {
    'jira_name': 'slack_name',
}


jira_url = ''
jira_login = ''
jira_password = ''
jira_jql = ''
