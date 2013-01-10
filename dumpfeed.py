#!/usr/bin/env python

# 2013-01-10

# Dump the contents of the feed with the name
#   given on the command line -- match is not case-sensitive.
#
#   Format is
#              TITLE :: DESCRIPTION

from newsfeed import ContentItem, NewsWire, SearchWire, config_file

import os, sys, string, pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(config_file, 'rb'))

try: name = sys.argv[1]
except:
	print("Please supply a feed name.")
	sys.exit(1)

for f in newsfeeds:
	if f.name.lower() == name.lower():
		for x in f.content:
			print(x.title, "::", x.descr)
