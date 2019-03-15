from setuptools import setup

setup(
    name='snap-o-nator-3000',
    version='0.1',
    author="Martin Jarosinski",
    author_email='marcin.jarosinski@gmail.com',
    description="Tool to manage EC2 instance snapshots",
    license="GPLv3+",
    packages=['snap'],
    url='https://github.com/mars0007/snap-o-nator-3000',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
    [console_scripts]
    snap=snap.snap:cli
    ''',
)
