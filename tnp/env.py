import os

from dotenv import load_dotenv

load_dotenv()


def _from_env_key(key):
    env_key = ('tnp_' + key).upper()
    val = os.getenv(env_key)
    if not val:
        raise ValueError(f'{env_key} must be set')
    return val


def get_project():
    return _from_env_key('project')


def get_project_option():
    return '--project {}'.format(get_project())


def get_bucket_uri():
    return 'gs://{}'.format(_from_env_key('bucket'))
