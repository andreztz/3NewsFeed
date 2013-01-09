#!/usr/bin/env python

# 2013-01-09

# Print the number of bytes occupied by the contents of each feed

# Usage: bsize [minimum size in bytes]

from newsfeed import NewsWire, SearchWire, config_file, console_encoding

import sys, time, pickle

try:    min_size = int(sys.argv[1])
except: min_size = 10000		# default minimum size reported


newsfeeds, config = pickle.load(open(config_file, 'rb'))

res = []

for f in newsfeeds:
	if not isinstance(f, SearchWire):
		name = f.name
		#if type(name) == type(""):
		#	name = name.encode(console_encoding, 'replace')
		size = 0
		for n in f.content:
			size += (len(n.title) + len(n.descr) + len(n.link)
				 + len(n.date) + len(n.fromfeed))
		size += len(list(f.headlines.keys())) * (len(list(f.headlines.keys())[0]) + 8)
		if f.lastresult != None:
			size += len(f.lastresult)
		try: size += len(f.webpage)
		except: pass
		res.append( [name, size] )

res.sort(key=lambda r: r[1])

print()
print("%30s  |  %s" % ("Feed name", "Size (bytes)"))
print(74 * '=')

s = 0

for x, y in res:
	if y > min_size:
		print("%30s  |  %u" % (x[:30], int(y)))
		s += int(y)

print(74 * '=')
print("%30s  |  %u" % ('Total', s))
print()
