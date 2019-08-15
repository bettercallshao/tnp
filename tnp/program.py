# -*- coding: future_fstrings -*-
from invoke import Collection, Program

from . import pipe, secret, version

ns = Collection()
ns.add_collection(secret.ns, 'secret')
ns.add_collection(pipe.ns, 'pipe')

program = Program(namespace=ns, version=version)
