#!/usr/bin/env python

# 2013-01-09

# Export marked items to XHTML file (prints to standard output).
#   Usage: ./export_flagged.py  > flagged.html

import newsfeed

import pickle

newfeeds = []
config   = {}

newsfeeds, config = pickle.load(open(newsfeed.config_file, 'rb'))

h1 = 'NewsFeed — Important Items'
numbered = True


print("""<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>%s</title>
</head>
<body>
<h1>%s</h1>""" % (h1, h1))


for i, f in enumerate(newsfeeds):
	if isinstance(f, newsfeed.Marked_items):
		def so(q):
			return newsfeeds[i].headlines.get(newsfeed.gethash(q.title, q.descr), 0)

		sortcontent = f.content
		sortcontent.sort(key=lambda r: so(r))

		for n, x in enumerate(sortcontent):
			if numbered:
				num = '[%u/%u]' % (n + 1, len(sortcontent))
			else: num = ''
			print('<small>%s</small><h2><a href="%s">%s</a> (%s)</h2>' % (num, x.link, x.title, x.fromfeed))
			print('<h3>%s</h3>' % x.date)
			print('%s' % x.descr)
			print('<h3>%s</h3><hr />' % x.link)
			
print('</body></html>')
