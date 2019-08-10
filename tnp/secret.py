import re
from uuid import uuid4

from invoke import Collection, task

from .env import get_bucket_uri, get_project_option

KEYRING = KEY = 'tnp'
ENV = 'env'
FILE = 'file'
SECRETS = 'secrets'


@task
def create_kms(c):
    c.run(' '.join([
        f'gcloud kms keyrings create {KEYRING}',
        get_project_option(),
        f'--location=global',
    ]), echo=True)
    c.run(' '.join([
        f'gcloud kms keys create {KEY}',
        get_project_option(),
        f'--location=global',
        f'--keyring={KEYRING}',
        f'--purpose=encryption',
    ]), echo=True)


def get_kms_option():
    return ' '.join([
        f'--key={KEY}',
        f'--keyring={KEYRING}',
        f'--location=global',
    ])


def upload_data(c, key, data, prefix):
    assert re.match('[A-Z0-9]+', key), 'key only accepts A-Z, 0-9, _'

    plain = '/tmp/' + str(uuid4())
    cipher = '/tmp/' + str(uuid4())
    bucket_uri = get_bucket_uri()

    with open(plain, 'w') as f:
        f.write(data)

    c.run(' '.join([
        f'gcloud kms encrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file={plain}',
        f'--ciphertext-file=-',
        f'| base64 -w 0 > {cipher}',
        f'&& gsutil cp {cipher} {bucket_uri}/{SECRETS}/{prefix}/{key}',
        f'&& rm {plain} {cipher}',
    ]), echo=True)


def download_data(c, key, prefix):
    bucket_uri = get_bucket_uri()
    res = c.run(' '.join([
        f'gsutil cat {bucket_uri}/{SECRETS}/{prefix}/{key}',
        f'| base64 -d',
        f'| gcloud kms decrypt',
        get_project_option(),
        get_kms_option(),
        f'--plaintext-file=-',
        f'--ciphertext-file=-',
    ]), echo=True, hide='stdout')
    return res.stdout


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
    data = download_data(c, key, ENV)
    c.run(f'echo {data} | base64 -d', echo=False)


@task
def ls(c):
    bucket_uri = get_bucket_uri()
    c.run(f'gsutil ls {bucket_uri}/{SECRETS}/**', echo=True)


ns = Collection()
ns.add_task(create_kms)
ns.add_task(set_env)
ns.add_task(get_env)
ns.add_task(set_file)
ns.add_task(get_file)
ns.add_task(ls)
