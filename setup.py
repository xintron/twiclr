#!/usr/bin/env python2
from setuptools import setup

entry_points = {
    'console_scripts': [
        'twiclr = twiclr.main:main'
    ]
}

setup(
    name='twiclr',
    version='0.1.0',
    url='https://github.com/xintron/twiclr',
    license = 'BSD License',
    author = 'Marcus Carlsson',
    author_email = 'carlsson.marcus@gmail.com',
    description = 'Terminal Twitter-client',
    packages = ['twiclr'],
    install_requires = [
        'oauth2>=0.7.4',
        'twython>=2.3.2',
        'urwid>=1.0.1',
    ],
    entry_points = entry_points,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
