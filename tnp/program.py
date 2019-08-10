from invoke import Collection, Program

from . import secret, spec, version

ns = Collection()
ns.add_collection(secret.ns, 'secret')
ns.add_collection(spec.ns, 'spec')

program = Program(namespace=ns, version=version)
