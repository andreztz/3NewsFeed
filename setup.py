#!/usr/bin/env python

from distutils.core import setup

setup(name="NewsFeed",
        version="3.3",
        description="A reader and aggregator for RSS/RDF/Atom feeds in Python/Tk",
        author="Martin C. Doege",
        author_email="mdoege@compuserve.com",
	url="http://mdoege.github.io/3NewsFeed/",
        py_modules=["newsfeed", "rssfinder", "feedparser", "dlthreads", "play_wav", "sgmllib3"],
	scripts=["newsfeed", "Start_NewsFeed.py", "add_feed.py", "feed2opml.py", "opml2feed.py", "dumpfeed.py", "update_feeds.py", "dinos.py", "bsize.py", "export_flagged.py", "export_unread.py"],
	data_files=[('sounds', ['email.wav'])] )
