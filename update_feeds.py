#!/usr/bin/env python

# 2006-01-26

# Update NewsFeed's feed database from the commandline.

# Usage: update_feeds.py

# Note: If NewsFeed is running at the same time, it may overwrite the changes.
#       Then again, is NewsFeed is running, you don't need the script.

#       So the suggestion is to execute this script in a cron job so that
#       feeds stay updated even when NewsFeed is not running. No harm should
#       be done if NewsFeed happens to be running.

from newsfeed import *


try:
	pid = open(pid_file, 'r').read()
	if len(sys.argv) == 2 and sys.argv[1] == '-v':
		print "NewsFeed is currently running under PID %s, aborting update.\n" % pid
except:
	newsfeeds, config = cPickle.load(open(config_file, 'rb'))

	for f in [x for x in newsfeeds if not isinstance(x, SearchWire)]:
		f.u_time = approx_time()

	for f in [x for x in newsfeeds if not isinstance(x, SearchWire)]:
		f.get_news(refresh = True)

	for fs in [x for x in newsfeeds if isinstance(x, SearchWire)]:
		fs.get_news(refresh = True)

	try: cPickle.dump((newsfeeds, config), open(config_file, 'wb'), 1)
	except:
		sys.stderr.write("Error: Writing cache file failed.\n")
		sys.exit(2)
