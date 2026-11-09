"""Validate Beta requests before running any private source code."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def read_request(path):
    if path.stat().st_size > 4096:
        raise ValueError('Beta request exceeds the size limit')

    request = json.loads(path.read_text())

    if request.get('repository') != 'gridness/tianra':
        raise ValueError('Unexpected source repository')

    for name in ('source', 'base'):
        if not re.fullmatch('[a-f0-9]{40}', request.get(name, '')):
            raise ValueError('Expected a full source commit')

    for name in ('run_number', 'run_id', 'run_attempt'):
        if type(request.get(name)) is not int or not 0 < request[name] < 10 ** 15:
            raise ValueError('Invalid private workflow run identity')

    return request


def verify_source(source):
    if not re.fullmatch('[a-f0-9]{40}', source):
        raise ValueError('Expected a full source commit')

    head = subprocess.check_output(['git', '-C', 'source', 'rev-parse', 'HEAD'], text=True).strip()

    if head != source:
        raise ValueError('The checkout differs from the requested source')

    # ASVS 8.3.1: only private main history is eligible for production publication.
    subprocess.run(
        ['git', '-C', 'source', 'merge-base', '--is-ancestor', source, 'origin/main'],
        check=True,
    )


if __name__ == '__main__':
    if sys.argv[1:] == ['read']:
        request = read_request(Path('requests/beta.json'))

        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            for name, value in request.items():
                output.write(f'{name}={value}\n')
    elif len(sys.argv) == 3 and sys.argv[1] == 'verify':
        verify_source(sys.argv[2])
    else:
        raise ValueError('Expected read or verify SOURCE_SHA')
