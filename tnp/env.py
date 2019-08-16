# -*- coding: future_fstrings -*-
import os

from dotenv import load_dotenv

load_dotenv()


def get_env_key(key):
    return ('tnp_' + key).upper()


def get_val(key):
    env_key = get_env_key(key)
    val = os.getenv(env_key)
    if not val:
        raise ValueError(f'{env_key} must be set')
    return val


def get_project():
    return get_val('project')


def get_project_option():
    return '--project={}'.format(get_project())


def get_region_option():
    return '--region={}'.format(get_val('region'))


def get_bucket_uri():
    return 'gs://{}'.format(get_val('bucket'))


def get_set_vars_arg():
    return ','.join(
        get_env_key(key) + '=' + get_val(key)
        for key in ('project', 'bucket'))


def get_tag():
    return 'gcr.io/{}/tnp'.format(get_project())
