import utils
import config


def strip_issue(issue):
    return {
        'url': '{}/browse/{}'.format(config.jira_url, issue['key']),
        'summary': issue['fields']['summary'],
        'assignee': issue['fields']['assignee']['name'],
        'status': issue['fields']['status']['name'],
    }


def string_template(item):
    return '{url} {summary} @{assignee} `{status}`'.format(
        url=item['url'],
        summary=item['summary'],
        assignee=config.jira_slack_mapping.get(item['assignee'], item['assignee']).lower(),
        status=item['status']
    )


def get():
    response = utils.make_request(
        'POST',
        '{}/rest/api/2/search'.format(config.jira_url),
        auth=(config.jira_login, config.jira_password),
        json={
            "jql": config.jira_jql,
            "fields": ["summary", "status", "assignee"]
        },
    )
    return response


def get_issues():
    result = get()['issues']
    if not result:
        return None
    result = (strip_issue(x) for x in result)
    result = '*Stuck issues*\n' + '\n'.join([string_template(x) for x in result])
    return result
