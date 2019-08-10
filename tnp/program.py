from invoke import Collection, Program

from . import secret, version

ns = Collection()
ns.add_collection(secret.ns, 'secret')

program = Program(namespace=ns, version=version)
