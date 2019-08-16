# -*- coding: future_fstrings -*-
import os

import yaml
from flask import Flask
from invoke import Collection, task

from . import pipe
from .env import (get_project_option, get_region_option, get_set_vars_arg,
                  get_tag)

app = Flask('tnp')


@app.route('/', methods=['GET'])
def get():
    return 'tnp server is up'


@app.route('/<name>', methods=['POST'])
def run(name):
    res = pipe.run(app.c, name, [])
    return res.stdout


@task
def up(c):
    app.c = c
    app.run(host='0.0.0.0', port=os.getenv('PORT', '8080'))


@task
def deploy(c):
    tag = get_tag()
    c.run(f'docker tag hydiant/tnp {tag} && docker push {tag}')
    c.run(' '.join([
        f'gcloud beta run deploy tnp',
        get_project_option(),
        get_region_option(),
        f'--image {tag}',
        f'--platform=managed',
        f'--no-allow-unauthenticated',
        f'--concurrency=1',
        f'--set-env-vars=' + get_set_vars_arg(),
    ]))


@task
def url(c):
    res = c.run(' '.join([
        f'gcloud beta run services describe tnp',
        get_project_option(),
        get_region_option(),
        '--platform=managed',
    ]), hide='stdout')
    return yaml.safe_load(res.stdout)['status']['url']


ns = Collection(up, deploy, url)
ns.configure({'run': {'echo': True}})
