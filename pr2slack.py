from itertools import chain
import sys
import requests


ACCESS_TOKEN = sys.argv[1]
SLACK_WEBHOOK_URL = sys.argv[2]
BASE_URL = 'https://api.github.com/repos/truckerpath/{repo}'
PR_URL = BASE_URL + '/pulls'
REVIEWS_URL = BASE_URL + '/pulls/{number}/reviews'
REQUESTED_REVIEWERS_URL = BASE_URL + '/pulls/{number}/requested_reviewers'
ISSUE_URL = BASE_URL + '/issues/{number}'

REVIEWS_HEADERS = {
    'Accept': 'application/vnd.github.black-cat-preview+json',
}

HEADERS = {
    'user-agent': 'pr2slack',
    'Authorization': 'token {}'.format(ACCESS_TOKEN),
}

DEBUG_CHANNEL = '' # channel where to send Exceptions raised by this script. @username is acceptable.

REPOS = {
    # list of repo names
}

GUYS = {
   # list of github usernames to react on
}

GITHUB_SLACK_MAP = {
    # optional mapping of github usernames to slack ones
}


def get(url, params=None, headers=None):
    if headers is None:
        headers = {}
    response = requests.get(url, params, headers=dict(**HEADERS, **headers))
    response.raise_for_status()
    return response.json()


def extract(pull_request):
    return {
        'repo': pull_request['head']['repo']['name'],
        'number': pull_request['number'],
        'url': pull_request['html_url'],
        'author': pull_request['user']['login'],
    }


def our_guy(pull_request):
    return pull_request['author'] in GUYS


def not_pending(issue):
    return 'pending' not in (label['name'] for label in get(ISSUE_URL.format(**issue))['labels'])


def get_requested_reviewers(pull_request):
    return {
        'author': pull_request['author'],
        'url': pull_request['url'],
        'requested': (
            requested_reviewers['login']
            for requested_reviewers in get(REQUESTED_REVIEWERS_URL.format(**pull_request), headers=REVIEWS_HEADERS)
        ),
    }


def not_approved(pull_request):
    return 'APPROVED' not in (
        reviewer['state']
        for reviewer in get(REVIEWS_URL.format(**pull_request), headers=REVIEWS_HEADERS)
    )


def get_prs(repo):
    return get(PR_URL.format(repo=repo), params={'status': 'open'})


def string_template(item):
    return '{url} by @{author} for {requested}'.format(
        author=item['author'].lower(),
        url=item['url'],
        requested=' '.join(
            '@{}'.format(GITHUB_SLACK_MAP.get(username, username)).lower() for username in item['requested']
        ) or '*nobody*'
    )


def slack(data):
    requests.post(SLACK_WEBHOOK_URL, json={
        'text': 'Psst,\n' + data,
        'username': 'pull requests alert',
        'icon_emoji': ':octopus:',
        'link_names': 1,
    }).raise_for_status()


try:
    result = (get_prs(x) for x in REPOS)
    result = chain(*result)
    result = (extract(x) for x in result)
    result = (x for x in result if our_guy(x) and not_pending(x) and not_approved(x))
    result = (get_requested_reviewers(x) for x in result)
    result = (string_template(x) for x in result)
    slack('\n'.join(result))
except Exception as any_error:
    requests.post(SLACK_WEBHOOK_URL, json={
        'text': '\n'.join(str(x) for x in [type(any_error), any_error]),
        'channel': DEBUG_CHANNEL,
        'username': 'pull requests alert',
        'icon_emoji': ':octopus:',
    })
