import re

from invoke import Collection, task

from .env import get_bucket_uri, get_project, get_project_option

KEYRING = KEY = 'tnp'
ENV = 'env'
FILE = 'file'
SECRETS_URI = get_bucket_uri() + '/secrets'


def get_kms_uri():
    project = get_project()
    return (f'projects/{project}/locations/global/' +
            f'keyRings/{KEYRING}/cryptoKeys/{KEY}')


@task
def create_kms(c):
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

    c.run(' '.join([
        f'printf $DATA',
        f'| gcloud kms encrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file=-',
        f'--ciphertext-file=-',
        f'| base64 -w 0',
        f'| gsutil cp - {SECRETS_URI}/{prefix}/{key}',
    ]), env={'DATA': data})


def download_data(c, key, prefix):
    res = c.run(' '.join([
        f'gsutil cat {SECRETS_URI}/{prefix}/{key}',
        f'| base64 -d',
        f'| gcloud kms decrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file=-',
        f'--ciphertext-file=-',
    ]), hide='stdout')
    return res.stdout


def download_enc(c, key, prefix):
    res = c.run(
        f'gsutil cat {SECRETS_URI}/{prefix}/{key}',
        hide='stdout')
    return res.stdout


def get_enc_env(c, key):
    return download_enc(c, key, ENV)


def get_enc_file(c, key):
    return download_enc(c, key, FILE)


@task
def set_env(c, key, data):
    upload_data(c, key, data, ENV)


@task
def set_file(c, key, path):
    res = c.run(f'cat {path} | base64 -w 0', hide='stdout')
    data = res.stdout.strip()

    upload_data(c, key, data, FILE)


@task
def get_env(c, key):
    print(download_data(c, key, ENV))


@task
def get_file(c, key):
    data = download_data(c, key, FILE)
    c.run(f'printf $DATA | base64 -d', env={'DATA': data})


@task
def ls(c):
    c.run(f'gsutil ls {SECRETS_URI}/**')


@task
def file_from_env(c, key, path):
    c.run(f'printf ${key} | base64 -d > {path}')


ns = Collection(create_kms, set_env, get_env, set_file, get_file, ls,
                file_from_env)
ns.configure({'run': {'echo': True}})
