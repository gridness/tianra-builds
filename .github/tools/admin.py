"""Select trusted Admin source and find its last successful validation."""
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from request import read_request

REPOSITORY = 'gridness/tianra-builds'


def source_commit(value):
    # ASVS 2.2.1: validate before checkout, output or subprocess arguments.
    if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{40}', value):
        raise ValueError('Expected a full private source commit.')

    return value


def api(*args):
    # ASVS 1.2.5: GitHub parameters remain separate arguments.
    result = subprocess.check_output(['gh', 'api', *args], text=True)

    return json.loads(result)


def successful_source():
    runs = api(
        '--method', 'GET', f'repos/{REPOSITORY}/actions/workflows/admin-release.yml/runs',
        '-f', 'branch=main', '-f', 'status=success', '-f', 'per_page=1',
    )['workflow_runs']

    if not runs:
        return ''

    run = runs[0]

    if run['event'] == 'workflow_dispatch':
        title = re.fullmatch(r'Admin ([a-f0-9]{40})', run['display_title'])

        if not title:
            raise ValueError('The successful Admin run has no valid source identity.')

        return source_commit(title[1])

    if run['event'] != 'push':
        raise ValueError('Unexpected Admin workflow trigger.')

    head = source_commit(run['head_sha'])
    request = api(f'repos/{REPOSITORY}/contents/requests/beta.json?ref={head}')
    content = json.loads(base64.b64decode(request['content']))

    if content.get('repository') != 'gridness/tianra':
        raise ValueError('Unexpected successful Admin source repository.')

    return source_commit(content.get('source'))


if __name__ == '__main__':
    command = sys.argv[1:]

    if command == ['select']:
        if os.environ['GITHUB_EVENT_NAME'] == 'workflow_dispatch':
            source = source_commit(os.environ.get('SOURCE_SHA', ''))
        else:
            source = read_request(Path('requests/beta.json'))['source']

        name, value = 'source', source
    elif command == ['baseline']:
        name, value = 'base', successful_source()
    else:
        raise ValueError('Expected select or baseline.')

    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write(f'{name}={value}\n')
