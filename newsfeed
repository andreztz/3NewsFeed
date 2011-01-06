#!/usr/bin/env python

"""
Newsfeed wrapper script (like Start_NewsFeed.py, but without the extension)

A Python/Tk RSS/RDF/Atom news aggregator. See included README.html for documentation.

Martin Doege, 2011-01-03

"""

import sys

assert sys.version >= '2.3', "This program has not been tested with older versions of Python. Please install Python 2.3 or greater."

nogui = '--nogui' in sys.argv

if __name__ == '__main__':
	from newsfeed import *

	try: main(nogui = nogui)
	finally:
		try: os.unlink(pid_file)
		except: pass
		save()
