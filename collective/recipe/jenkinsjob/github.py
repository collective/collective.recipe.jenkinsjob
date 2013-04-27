from requests.auth import HTTPBasicAuth

import sys
import json
import requests

GH_URL = 'https://api.github.com'


def create_hook(jenkins_url, jenkins_username, jenkins_password,
                github_username, github_password, jobname,
                github_project=None, github_hook_url=None):
    hook_url = \
        'https://%s:%s@%s/job/%s/build' % (
        jenkins_username,
        jenkins_password,
        jenkins_url,
        jobname,
    )
    req = {
        'name': 'web',
        'active': True,
        'config': {
            'url': hook_url,
            'insecure_ssl': 1,
        }
    }
    if not github_hook_url:
        github_hook_url = GH_URL + '/repos/%s/%s/hooks' % (
            github_username,
            github_project,
        )
    auth = HTTPBasicAuth(github_username, github_password)
    response = requests.post(url=github_hook_url, data=json.dumps(req), auth=auth)
    if response.status_code == 201:
        sys.stdout.write("Github post-commit hook created.\n")
    elif response.status_code == 422:
        sys.stdout.write("Github post-commit hook already exists.\n")
    else:
        sys.stdout.write("Github post-commit hook creation failed!\n")
