#!/usr/bin/env python

import sys

if sys.version_info < (3, 2):
    sys.exit('Sorry, Python < 3.2 is not supported')

from setuptools import setup
import versioneer

setup(
    name='diff-tester',
    description='Test harness that verifies a set of files output by the tested program against a reference set',
    author='Kyrylo Shpytsya',
    author_email='kshpitsa@gmail.com',
    url='https://github.com/kshpytsya/diff-tester',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
    ],
    package_dir={'': 'src'},
    packages=['diff_tester'],
    entry_points={
        'console_scripts': [
            'diff-tester = diff_tester.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Bug Tracking',
    ],
)
