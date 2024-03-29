# -*- coding: future_fstrings -*-
import re

from invoke import Collection, task

from .env import get_bucket_uri, get_project, get_project_option

KEYRING = KEY = 'tnp'
ENV = 'env'
FILE = 'file'


def get_secrets_uri():
    return get_bucket_uri() + '/secrets'


def get_kms_uri():
    project = get_project()
    return (f'projects/{project}/locations/global/' +
            f'keyRings/{KEYRING}/cryptoKeys/{KEY}')


@task
def create_kms(c):
    """Create a predefined KMS for pipes"""

    c.run(' '.join([
        f'gcloud kms keyrings create {KEYRING}',
        get_project_option(),
        f'--location=global',
    ]))
    c.run(' '.join([
        f'gcloud kms keys create {KEY}',
        get_project_option(),
        f'--location=global',
        f'--keyring={KEYRING}',
        f'--purpose=encryption',
    ]))


def get_kms_option():
    return ' '.join([
        f'--key={KEY}',
        f'--keyring={KEYRING}',
        f'--location=global',
    ])


def upload_data(c, key, data, prefix):
    assert re.match('[A-Z0-9]+', key), 'key only accepts A-Z, 0-9, _'

    secrets_uri = get_secrets_uri()
    c.run(' '.join([
        f'printf $DATA',
        f'| gcloud kms encrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file=-',
        f'--ciphertext-file=-',
        f'| base64 -w 0',
        f'| gsutil cp - {secrets_uri}/{prefix}/{key}',
    ]), env={'DATA': data})


def download_data(c, key, prefix):
    secrets_uri = get_secrets_uri()
    res = c.run(' '.join([
        f'gsutil cat {secrets_uri}/{prefix}/{key}',
        f'| base64 -d',
        f'| gcloud kms decrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file=-',
        f'--ciphertext-file=-',
    ]), hide='stdout')
    return res.stdout


def download_enc(c, key, prefix):
    secrets_uri = get_secrets_uri()
    res = c.run(
        f'gsutil cat {secrets_uri}/{prefix}/{key}',
        hide='stdout')
    return res.stdout


def get_enc_env(c, key):
    return download_enc(c, key, ENV)


def get_enc_file(c, key):
    return download_enc(c, key, FILE)


@task(help={'key': 'Variable name of the environment variable',
            'data': 'Content of the environment variable'})
def set_env(c, key, data):
    """Set a secret environment variable"""

    upload_data(c, key, data, ENV)


@task(help={'key': 'Identifier of the secret file',
            'path': 'Path of the file to use as secret'})
def set_file(c, key, path):
    """Set a secret file"""

    res = c.run(f'cat {path} | base64 -w 0', hide='stdout')
    data = res.stdout.strip()

    upload_data(c, key, data, FILE)


@task(help={'key': 'Variable name of the environment variable'})
def get_env(c, key):
    """Get (print) a secret environment variable"""

    print(download_data(c, key, ENV))


@task(help={'key': 'Identifier of the secret file'})
def get_file(c, key):
    """Get (print) a secret file"""

    data = download_data(c, key, FILE)
    c.run(f'printf $DATA | base64 -d', env={'DATA': data})


@task
def ls(c):
    """List secrets uploaded on remote"""

    secrets_uri = get_secrets_uri()
    c.run(f'gsutil ls {secrets_uri}/**')


@task(help={'key': 'Identifier of the secret file',
            'path': 'Output path of secret file'})
def file_from_env(c, key, path):
    """[INTERNAL] Convert a environment variable to a file"""

    c.run(f'printf ${key} | base64 -d > {path}')


ns = Collection(create_kms, set_env, get_env, set_file, get_file, ls,
                file_from_env)
ns.configure({'run': {'echo': True}})
