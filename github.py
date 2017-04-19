import re
import config
import utils


def get(url):
    return utils.make_request('GET', url, headers={
        'user-agent': config.gh_user_agent,
        'Authorization': 'token {}'.format(config.gh_token),
        'Accept': 'application/vnd.github.black-cat-preview+json',
    })


def strip_data(search_result_item):
    task = search_result_item['title']
    task_match = re.match('[A-Z]+-[0-9]+', task)
    if task_match:
        task = task_match.group(0)

    return {
        'task': task,
        'url': search_result_item['pull_request']['url'],
        'html_url': search_result_item['html_url'],
        'author': search_result_item['user']['login'],
    }


def add_reviews(pull_request):
    reviews = get(pull_request['url'] + '/reviews')
    requested = get(pull_request['url'] + '/requested_reviewers')
    users = {(item['user']['login'], item['state']) for item in reviews}
    users = users | {(reviewer['login'], 'REQUESTED') for reviewer in requested}
    item = {
        'participants': {user[0] for user in users} - {pull_request['author']},
        'is_approved': 'APPROVED' in (user[1] for user in users),
    }
    item.update(pull_request)
    return item


def string_template(item):
    return '{task} {url} @{author} > {reviewers}'.format(
        task=item['task'],
        url=item['html_url'],
        author=item['author'].lower(),
        reviewers=' '.join(
            '@{}'.format(config.gh_slack_mapping.get(username, username)).lower() for username in item['participants']
        ) or '*nobody*'
    )


def get_prs():
    result = get(config.gh_search_url)['items']
    result = (strip_data(x) for x in result)
    result = (add_reviews(x) for x in result)
    result = (x for x in result if not x['is_approved'])
    result = list(result)
    if not result:
        return None
    result = 'Pending PRs:\n' + '\n'.join([string_template(x) for x in result])
    return result
