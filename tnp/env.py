import os

keys = {'project', 'bucket'}


def _from_env_key(key):
    env_key = ('tnp_' + key).upper()
    val = os.getenv(env_key)
    if not val:
        raise ValueError(f'{env_key} must be set')
    return val


def get_env():
    env = {}
    for key in keys:
        env[key] = _from_env_key(key)
    return env


def get_project_option():
    return '--project {}'.format(get_env()['project'])


def get_bucket_uri():
    return 'gs://{}'.format(get_env()['bucket'])
