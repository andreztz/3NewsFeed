#!/usr/bin/env python

# 2006-01-26

# Add feeds from OPML file to NewsFeed database.

# Usage: ./opml2feed.py thefeeds.opml

# Important:
#   * NewsFeed must have been run at least once (so that ~/.newsfeed has been created).
#   * NewsFeed should not be running while using opml2feed, or it will overwrite the
#     changes on exit.
#   * Due to an apparent Python bug, opml2feed has to remove search feeds from the database.
#     Sorry, but you will have to recreate them. (The "Recently Visited" and "Important Items"
#     feeds are recreated automatically the next time NewsFeed is started.)


from newsfeed import ContentItem, NewsWire, SearchWire, config_file

import os, sys, string, pickle, fileinput, xml.sax

from xml.sax.handler import *

newsfeeds = []
config    = {}
num   = 0
total = 0

newsfeeds, config = pickle.load(open(config_file, 'rb'))

class OPMLHandler(ContentHandler):
	def startElement(s, n, a):
		global newsfeeds, urls, num, total

		total += 1
		name = string.replace(a.get('title') or a.get('text', "?"), '\\"', '"')
		url  = a.get('xmlurl') or a.get('xmlUrl') or a.get('url', "http://")
		homeurl = a.get('htmlurl') or a.get('htmlUrl') or "http://"

		if url not in urls or url == "http://":
			newsfeeds.append(NewsWire(name = name, url  = url, homeurl = homeurl,
				refresh = config['refresh_every'], expire = config['maxtime']))
			num += 1

newsfeeds = [x for x in newsfeeds if not isinstance(x, SearchWire)]
urls = []
for x in newsfeeds: urls += [x.url]

h = OPMLHandler()
if len(sys.argv) < 2:
	sys.stderr.write("Please supply a filename on the commandline.\n")
	sys.exit(1)
xml.sax.parse(sys.argv[1], h)

print("Added %u new feeds from a total of %u." % (num, total))

pickle.dump((newsfeeds, config), open(config_file, 'wb'), 1)

