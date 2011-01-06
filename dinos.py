#!/usr/bin/env python

# 2007-04-20

# Print the feeds that have not been updated in a long time,
#   sorted by the most recent item's download time in days.

# Usage: dinos.py [minimum age in days]


from newsfeed import NewsWire, SearchWire, config_file, console_encoding

import sys, time, cPickle

try:    min_age = int(sys.argv[1])
except: min_age = 10			# default minimum age of a feed in days
					#   for it to be considered a dinosaur

def comp(x, y):
	"Compare two items by time."
	if x[1] - y[1] < 0: return 1
	else: return -1


newsfeeds, config = cPickle.load(open(config_file, 'rb'))

t = time.time()
res = []

for f in newsfeeds:
	if not isinstance(f, SearchWire):
		try: v = max(f.headlines.values())
		except: continue
		name = f.name
		if type(name) == type(u""):
			name = name.encode(console_encoding, 'replace')
		res.append( [name, (t - v) / 86400.] )

res.sort(comp)

print
print "%30s  |  %s" % ("Feed name", "# of days since download of latest item")
print 74 * '='

for x, y in res:
	if y > min_age: print "%30s  |  %u" % (x[:30], int(y))

print
