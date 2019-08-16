# -*- coding: future_fstrings -*-
import yaml
from invoke import task

SPEC_PATH = 'tnp.yaml'
DEFAULT_SPEC = """
name: echo
cron: "* 1 * * *"
cloudbuild: |
  timeout: 600s
  steps:
  - name: gcr.io/$PROJECT_ID/echo
    env:
    - ECHO_PARAM={{ ECHO_PARAM }}
    - ECHO_SECRET_FILE_PATH=secret.txt
    secretEnv:
    - ECHO_SECRET_ENV
parameters:
  secret_env:
  - key: ECHO_SECRET_ENV
  secret_file:
  - key: ECHO_SECRET_FILE
    path: secret.txt
  template:
  - key: ECHO_PARAM
    value: default_template_i_am
"""

COMPOSE_PATH = 'docker-compose.yaml'
DEFAULT_COMPOSE = """
version: '3'
services:
  echo:
    image: 'gcr.io/${TNP_PROJECT}/echo'
    build:
      context: echo
    environment:
    - ECHO_PARAM=this is echo param
    - ECHO_SECRET_ENV=this is echo secret env
    - ECHO_SECRET_FILE_PATH=main.py
"""

ECHO_DOCKER = """
FROM python:3.7-stretch

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "/work/main.py"]
"""
ECHO_MAIN = """
import pandas as pd
import requests
import os


def main():
    data = requests.get(
        'https://registry.hub.docker.com/v1/repositories/python/tags').content
    print('Data:')
    print(pd.read_json(data).describe())
    print('ECHO_PARAM: {}'.format(os.getenv('ECHO_PARAM')))
    print('ECHO_SECRET_ENV: {}'.format(os.getenv('ECHO_SECRET_ENV')))

    secret_file = os.getenv('ECHO_SECRET_FILE_PATH')
    print('ECHO_SECRET_FILE_PATH: {}'.format(secret_file))
    if secret_file:
        with open(secret_file) as f:
            print(f.read())


if __name__ == '__main__':
    main()
"""
ECHO_REQUIREMENTS = """
pandas
requests
"""


def file_from_str(data, path):
    with open(path, 'w') as f:
        f.write(data.lstrip())


def dict_from_file(path):
    with open(path) as f:
        return yaml.safe_load(f)


@task
def init(c):
    file_from_str(DEFAULT_SPEC, SPEC_PATH)
    file_from_str(DEFAULT_COMPOSE, COMPOSE_PATH)

    c.run('mkdir -p echo')
    file_from_str(ECHO_DOCKER, 'echo/Dockerfile')
    file_from_str(ECHO_MAIN, 'echo/main.py')
    file_from_str(ECHO_REQUIREMENTS, 'echo/requirements.txt')
