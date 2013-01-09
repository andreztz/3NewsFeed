#!/usr/bin/env python

# 2013-01-09

# Export unread items to XHTML file (prints to standard output).
#   Usage: ./export_unread.py  > unread.html

import newsfeed
import pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(newsfeed.config_file, 'rb'))

h1 = 'NewsFeed — Unread Items'
numbered = True


print("""<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>%s</title>
</head>
<body>
<h1>%s</h1>""" % (h1, h1))

unread = 0
items  = []

for i, f in enumerate(newsfeeds):
	if not isinstance(f, newsfeed.SearchWire):
		arr = [x for x in f.content if x.unread]
		unread += len(arr)
		items += arr

for n, x in enumerate(items):
	if numbered:
		num = '[%u/%u]' % (n + 1, unread)
	else: num = ''
	print('<small>%s</small><h2><a href="%s">%s</a> (%s)</h2>' % (num, x.link, x.title, x.fromfeed))
	print('<h3>%s</h3>' % x.date)
	print('%s' % x.descr)
	print('<h3>%s</h3><hr />' % x.link)
		
print('</body></html>')
