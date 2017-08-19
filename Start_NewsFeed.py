#!/usr/bin/env python

# NewsFeed is an RSS/RDF/Atom reader and aggregator.
# Copyright (C) 2003-2017  Martin C. Doege (mdoege@compuserve.com)
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

"""
Newsfeed wrapper script (like Start_NewsFeed.py, but without the extension)

A Python/Tk RSS/RDF/Atom news aggregator. See included README.html for documentation.

Martin Doege, 2013-01-10

"""

import sys

assert sys.version >= '3.3', "Please install Python 3.3 or later."

nogui = '--nogui' in sys.argv

if __name__ == '__main__':
	from newsfeed import *

	try: main(nogui = nogui)
	finally:
		try: os.unlink(pid_file)
		except: pass
		save()
