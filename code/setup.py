#!/usr/bin/env python

#     This file is part of wiki2beamer.
# wiki2beamer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# wiki2beamer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with wiki2beamer.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name='wiki2beamer',
    version='0.9.5',
    scripts=['wiki2beamer'],
    description='Create LaTeX-beamer presentations with a wiki syntax',
    author='Michael Rentzsch, Kai Dietrich and others',
    author_email='mmichael.rentzsch@repc.de, mail@cleeus.de',
    url='http://wiki2beamer.sourceforge.net/'
)
