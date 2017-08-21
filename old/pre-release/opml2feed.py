#!/usr/bin/env python

from newsfeed import ContentItem, NewsWire, SearchWire

import os, sys, string, cPickle, xmllib

newfeeds = []
config   = {}

config_file = os.path.join(os.path.expanduser("~"), ".newsfeed")

newsfeeds, config = cPickle.load(open(config_file, 'r'))

class OPMLParser(xmllib.XMLParser):
	def __init__(s):
		xmllib.XMLParser.__init__(s)
		
	def start_outline(s, a):
		newsfeeds.append(NewsWire(
		name = string.replace(a.get('title') or a.get('text', "?"), '\\"', '"'),
		url  = a.get('xmlurl') or a.get('xmlUrl') or a.get('url', "http://"),
		homeurl = a.get('htmlurl') or a.get('htmlUrl') or "http://",
		refresh = config['refresh_every'], expire = config['maxtime']))

newsfeeds = filter(lambda x: not isinstance(x, SearchWire), newsfeeds)

try: opml = open(sys.argv[1], 'r')
except Exception: sys.exit("Could not open file.")

p = OPMLParser()

p.feed(opml.read())

p.close()

cPickle.dump((newsfeeds, config), open(config_file, 'w'))
