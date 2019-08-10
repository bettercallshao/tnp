from setuptools import setup

from tnp import version

with open('README.md') as f:
    long_description = f.read()

setup(
    name='tnp',
    version=version,
    description='Practical pipelining on GCP.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Shaoqing Tan',
    author_email='tansq7@gmail.com',
    url='https://github.com/timlyrics/tnp',
    license='MIT',
    packages=['tnp'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['tnp=tnp.program:program.run'],
    },
)
