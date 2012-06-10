#!/usr/bin/env python

# 2005-01-26

# Add an URL to the NewsFeed database from the commandline.

# This could be used as a helper application e.g. to add a subscription by
# clicking an URL in the web browser.

# If NewsFeed is running, it will process the new URL and add a new entry
# at the end of its feed list.

# If it is not running, the new feed is added the next time it launches.

# Usage: add_feed.py http://www.theserver.com/therssfile.xml


import sys, os, signal
from newsfeed import config_file, addfeed_file, pid_file

if sys.platform == 'win32':
	sys.stderr.write("Sorry, this script does not work on Windows due to lack of signaling capabilities.\n")
	sys.exit(1)

feedurl = sys.argv[1]

if feedurl[0:len('feed://')] == 'feed://':
	feedurl = 'http://' + feedurl[len('feed://'):]

if feedurl[0:len('feed:')] == 'feed:':
	feedurl = feedurl[len('feed:'):]

print("Adding feed at", feedurl, "to the NewsFeed new entries file.")

open(addfeed_file, 'a').write(feedurl + '\n')

try:
	pid = open(pid_file, 'r').read()
	print("NewsFeed is currently running under PID %s." % pid)
	os.kill(int(pid), signal.SIGUSR1)
except: print("NewsFeed is not running, feeds will be read at next start.")
