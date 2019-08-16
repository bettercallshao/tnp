# -*- coding: future_fstrings -*-
import os
from uuid import uuid4

import yaml
from invoke import Collection, task
from jinja2 import Template

from .env import get_bucket_uri, get_project, get_project_option
from .init import init
from .secret import get_enc_env, get_enc_file, get_kms_uri
from .server import url as server_url

PARAMETERS = 'parameters'
SECRET_ENV = 'secret_env'
SECRET_FILE = 'secret_file'
TEMPLATE = 'template'
SPEC_PATH = 'tnp.yaml'


def get_pipes_uri():
    return get_bucket_uri() + '/pipes'


def get_spec():
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


def step_from_file(key, path):
    return {
        'name': 'hydiant/tnp',
        'args': [
            'secret.file-from-env',
            key,
            path,
        ],
        'secretEnv': [
            key,
        ],
    }


def secrets_from_dict(d):
    return [{
        'kmsKeyName': get_kms_uri(),
        'secretEnv': d,
    }]


@task
def deploy(c):
    spec = get_spec()
    name = spec['name']
    pipes_uri = get_pipes_uri()
    c.run(f'gsutil cp {SPEC_PATH} {pipes_uri}/{name}')

    cron = spec.get('cron')
    if cron:
        base = server_url(c)
        project = get_project()
        command = ' '.join([
            f'gcloud scheduler jobs update http {name}',
            get_project_option(),
            f'--schedule="{cron}"',
            f'--uri={base}/{name}',
            f'--http-method=POST',
            f'--oidc-service-account-email',
            f'{project}@appspot.gserviceaccount.com',
        ])
        c.run(command + ' || ' + command.replace('update', 'create'))


@task
def ls(c):
    pipes_uri = get_pipes_uri()
    c.run(f'gsutil ls {pipes_uri}')
    c.run(' '.join([
        f'gcloud scheduler jobs list',
        get_project_option(),
    ]))


@task
def status(c, name):
    c.run(' '.join([
        f'gcloud builds list --filter=tags:{name}',
        get_project_option(),
    ]))


def run_spec(c, spec, input_params):
    file_steps = []
    secerts_dict = {}
    params = spec.get(PARAMETERS, {})
    input_dict = dict(s.split('=') for s in input_params)

    for item in params.get(SECRET_ENV, []):
        secerts_dict[item['key']] = get_enc_env(c, item['key'])

    for item in params.get(SECRET_FILE, []):
        secerts_dict[item['key']] = get_enc_file(c, item['key'])
        file_steps.append(step_from_file(
            item['key'], item['path']))

    template = {
        item['key']: input_dict.get(item['key'], item['value'])
        for item in params.get(TEMPLATE, [])}

    cloudbuild = yaml.load(
        Template(spec['cloudbuild']).render(template))
    cloudbuild['steps'] = file_steps + cloudbuild['steps']
    cloudbuild['secrets'] = secrets_from_dict(secerts_dict)
    cloudbuild['tags'] = [spec['name']] + cloudbuild.get('tags', [])

    path = '/tmp/' + str(uuid4())
    with open(path, 'w') as f:
        yaml.dump(cloudbuild, f)
    res = c.run(' '.join([
        f'gcloud builds submit --no-source --async --config {path}',
        get_project_option(),
    ]))
    os.remove(path)
    return res


@task(iterable=['param'])
def run(c, name, param):
    pipes_uri = get_pipes_uri()
    res = c.run(f'gsutil cat {pipes_uri}/{name}', hide='stdout')
    spec = yaml.load(res.stdout)
    return run_spec(c, spec, param)


@task(iterable=['param'])
def run_local(c, param):
    spec = get_spec()
    return run_spec(c, spec, param)


ns = Collection(init, deploy, run, run_local, ls, status)
ns.configure({'run': {'echo': True}})
