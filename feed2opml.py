#!/usr/bin/env python

# 2007-04-23

# Dump NewsFeed database as an OPML file.

# Usage: ./feed2opml.py > myfeeds.opml


from newsfeed import ContentItem, NewsWire, SearchWire, config_file, console_encoding

import os, pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(config_file, 'rb'))
enc = console_encoding

print('<?xml version="1.0" encoding="%s"?>' % enc)
print('<opml version="1.0">\n<head><title>NewsFeed Bookmarks</title></head>\n<body>')

def mkfile(t):
	t = "".join([x for x in t if x.isalnum()][:16])
	return t.lower()

for i,f in enumerate(newsfeeds):
	if not isinstance(f, SearchWire):
		title = f.name.replace('"', '\\"').replace('&', '&amp;')
		if type(title) == type(""): title = title.encode(enc, "replace")
		name = f.name
		if type(name) == type(""): name = name.encode(enc, "replace")		
		url = f.url.replace('&', '&amp;')
		homeurl = f.homeurl.replace('&', '&amp;')
		fn = 'filename="%s%04u.xml"' % (mkfile(name), i + 1)
		print('<outline text="%s" title="%s" xmlUrl="%s" description="" type="rss" htmlUrl="%s" %s />' % (
			title, title, url, homeurl, fn))

print('</body></opml>')
