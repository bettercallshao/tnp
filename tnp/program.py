# -*- coding: future_fstrings -*-
from invoke import Collection, Program

from . import pipe, secret, server, version

ns = Collection()
ns.add_collection(secret.ns, 'secret')
ns.add_collection(pipe.ns, 'pipe')
ns.add_collection(server.ns, 'server')

program = Program(namespace=ns, version=version)
