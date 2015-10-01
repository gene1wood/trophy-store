import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='trophystore',
    version='0.1',
    packages=['trophystore'],
    include_package_data=True,
    license='MPL 2.0',
    description='A tool to manage, request, issue and automatically deploy '
        'certificates.',
    long_description=README,
    url='http://www.github.com/gene1wood/trophystore',
    author='Gene Wood',
    author_email='gene_wood@cementhorizon.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
    install_requires=['requests',
                      'boto>=2.24.0',
                      'Django',
                      'Jinja2',
                      'MySQL-python',
                      'pyOpenSSL',
                      'PyYAML',
                      'django-browserid'],
    entry_points={
        'console_scripts' :[
            'trophystore-manage = trophystore.utils:manage'
        ]
    }
)
