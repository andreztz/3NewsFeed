#!/usr/bin/env python

# 2007-02-26

# Export unread items to XHTML file (prints to standard output).
#   Usage: ./export_unread.py  > unread.html

import newsfeed
import pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(newsfeed.config_file, 'rb'))
enc = newsfeed.console_encoding

h1 = 'NewsFeed &mdash; Unread Items'
numbered = True


print('<?xml version="1.0" encoding="%s" ?>' % enc)
print("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
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

for x, n in zip(items, list(range(unread))):
	title = x.title.encode(enc, "replace")
	descr = x.descr.encode(enc, "replace")
	link  = x.link.encode(enc, "replace")
	date  = x.date.encode(enc, "replace")
	feed  = x.fromfeed.encode(enc, "replace")
	if numbered:
		num = '[%u/%u]' % (n + 1, unread)
	else: num = ''
	print('<small>%s</small><h2><a href="%s">%s</a> (%s)</h2>' % (num, link, title, feed))
	print('<h3>%s</h3>' % date)
	print('%s' % descr)
	print('<h3>%s</h3><hr />' % link)
		
print('</body></html>')
