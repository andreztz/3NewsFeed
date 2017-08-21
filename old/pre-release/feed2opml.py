#!/usr/bin/env python

from newsfeed import ContentItem, NewsWire, SearchWire

import os, string, cPickle

newfeeds = []
config   = {}

config_file = os.path.join(os.path.expanduser("~"), ".newsfeed")

newsfeeds, config = cPickle.load(open(config_file, 'r'))

print '<?xml version="1.0" encoding="ISO-8859-1"?>'
print '<opml version="1.0">\n<head><title>NewsFeeds Bookmarks</title></head>\n<body>'

def mkfile(t):
	t = string.replace(t, " ", "").lower()[0:16]
	t = string.replace(t, ",", "_")
	t = string.replace(t, ".", "_")
	return t

for f, i in zip(newsfeeds, range(len(newsfeeds))):
	if not isinstance(f, SearchWire):
		print '<outline title="%s" xmlurl="%s" htmlurl="%s" filename="%s%04u.xml" />' % (
						string.replace(f.name, '"', '\\"'), f.url, f.homeurl, mkfile(f.name), i + 1)

print '</body></opml>'
