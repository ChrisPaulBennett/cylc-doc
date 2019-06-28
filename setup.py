#!/usr/bin/env python
# coding=utf-8

# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2018 NIWA & British Crown (Met Office) & Contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

VERSION = "0.0.1"

INSTALL_REQUIRES = [
    'sphinx==2.0.*',
    'cylc-flow==8.0a0',
]

setup(
    name='Cylc Documentation',
    version=VERSION,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=INSTALL_REQUIRES,
    project_urls={
        "Documentation": "https://cylc.github.io/documentation.html",
        "Source": "https://github.com/cylc/cylc-doc",
        "Tracker": "https://github.com/cylc/cylc-doc/issues"
    }
)
