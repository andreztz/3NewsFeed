#!/usr/bin/env python

"""
Newsfeed wrapper script (like Start_NewsFeed.py, but without the extension)

A Python/Tk RSS/RDF/Atom news aggregator. See included README.html for documentation.

Martin Doege, 2013-01-09

"""

import sys

assert sys.version >= '3', "Please install Python 3."

nogui = '--nogui' in sys.argv

if __name__ == '__main__':
	from newsfeed import *

	try: main(nogui = nogui)
	finally:
		try: os.unlink(pid_file)
		except: pass
		save()
