import requests
import config


def make_request(method, url, **kwargs):
    if method == 'GET':
        response = requests.get(url, **kwargs)
    else:
        response = requests.post(url, **kwargs)
    print('GET {} {}'.format(response.status_code, response.url))
    response.raise_for_status()
    return response.json()


def send_to_slack(*args, debug_mode=False):
    message = '\n'.join([arg for arg in args if arg])
    if message:
        if debug_mode:
            return print('---\n{}'.format(message))
        requests.post(config.slack_webhook_url, json={
            'text': message,
            'username': 'pull requests alert',
            'icon_emoji': ':octopus:',
            'link_names': 1,
        }).raise_for_status()


def handle_error(error, debug_mode=False):
    text = '\n'.join(str(x) for x in [type(error), error])
    if debug_mode:
        return print(text)
    requests.post(config.slack_webhook_url, json={
        'text': text,
        'channel': config.slack_debug_channel,
        'username': 'watchmen',
        'icon_emoji': ':octopus:',
    })
