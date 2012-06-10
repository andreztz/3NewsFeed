#!/usr/bin/env python

# 2007-02-26

# Export marked items to XHTML file (prints to standard output).
#   Usage: ./export_flagged.py  > flagged.html

import newsfeed

import pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(newsfeed.config_file, 'rb'))
enc = newsfeed.console_encoding

h1 = 'NewsFeed &mdash; Important Items'
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


for i, f in enumerate(newsfeeds):
	if isinstance(f, newsfeed.Marked_items):
		def _by_time_order(x, y, i=i):
			a = newsfeeds[i].headlines.get(newsfeed.gethash(x.title, x.descr), 0)
			b = newsfeeds[i].headlines.get(newsfeed.gethash(y.title, y.descr), 0)
			c = x.title + x.fromfeed
			d = y.title + y.fromfeed
			if a == b:
				if c == d: return 0
				elif c > d: return 1
				else: return -1
			elif a < b: return 1
			else: return -1

		sortcontent = f.content
		sortcontent.sort(_by_time_order)

		for n, x in enumerate(sortcontent):
			title = x.title.encode(enc, "replace")
			descr = x.descr.encode(enc, "replace")
			link  = x.link.encode(enc, "replace")
			date  = x.date.encode(enc, "replace")
			feed  = x.fromfeed.encode(enc, "replace")
			if numbered:
				num = '[%u/%u]' % (n + 1, len(sortcontent))
			else: num = ''
			print('<small>%s</small><h2><a href="%s">%s</a> (%s)</h2>' % (num, link, title, feed))
			print('<h3>%s</h3>' % date)
			print('%s' % descr)
			print('<h3>%s</h3><hr />' % link)
			
print('</body></html>')
