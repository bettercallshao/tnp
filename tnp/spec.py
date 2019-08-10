import yaml
from invoke import Collection, task


SPEC_PATH = 'tnp.yaml'
DEFAULT_SPEC = """
m: 4
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
    - PARAM=this is echo from tnp!
"""

ECHO_DOCKER = """
FROM python:3.7-stretch

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""
ECHO_MAIN = """
import pandas as pd
import requests
import os


def main():
    data = requests.get(
        'https://registry.hub.docker.com/v1/repositories/python/tags').content
    print(pd.read_json(data).describe())
    print(os.getenv('PARAM'))


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


ns = Collection()
ns.add_task(init)
