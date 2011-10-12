# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       None
# mako:       False
#
#

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=['WebTest >= 1.2.3',
               'nose',
               'coverage',
               'wsgiref',
               'repoze.who-testutil >= 1.0.1',
               ]
install_requires=[
    "TurboGears2 >= 2.1.3",
    "Genshi",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2 >= 1.0a5",
    "sqlalchemy >= 0.7",
    "tw.forms",
    ]

if sys.version_info[:2] == (2,4):
    testpkgs.extend(['hashlib', 'pysqlite'])
    install_requires.extend(['hashlib', 'pysqlite'])

print install_requires

setup(
    name='Noodle-NG',
    version='1.5',
    description='File search engine',
    long_description='Noodle is a web search engine for local smb/cifs network shares (Windows/Samba).',
    author='The Noodle Developers',
    author_email='noodle-ng@googlegroups.com',
    url='https://code.google.com/p/noodle-ng/',
    license="GPL-3",
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'noodle': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'noodle': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = noodle.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
