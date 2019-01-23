#!/usr/bin/env python

from  Tkinter import *
import sys
assert sys.version >= '2.2', "This program has not been tested with older versions of Python. Please install Python 2.2 or greater."
import os, time, string, re, md5, webbrowser, cPickle
import rssparser, rssfinder, timeoutsocket

try: import tkSnack
except ImportError:
	print "'Snack' not installed, audio notification will not work."
	print " If you want it, get the module from http://www.speech.kth.se/snack/"
	tkSnack = None

# Setting this to a nonexistent filename will disable sound notification:
soundfile = "/usr/X11R6/share/gnome/sounds/email.wav"

# Program default values that cannot be changed via the GUI:
config = {}

config['mode']                     = "gui"
config['progname']                 = "NewsFeed"
config['refresh_every']            = 30		# Refresh interval in minutes
config['maxtime']                  = 30		# Maximum time (in days) to keep items

# Program default values that get saved automatically if changed:
config['geom_root']                = "900x600"  # Default
config['geom_info']                = "675x380"  #         window
config['geom_search']              = "350x200"  #                sizes
config['search_is_case_sensitive'] = 0          # Make new searches case sensitive?
config['search_match_whole_words'] = 0          # Match only entire words in searches?
config['search_only_unread']       = 0          # Search only in unread entries?

config_file = os.path.join(os.path.expanduser("~"), "." + config['progname'].lower())

newsfeeds = []

initial = [
  ("Wired News", "http://www.wired.com/news_drop/netcenter/netcenter.rdf"),
  ("NYT News",   "http://www.newsisfree.com/HPE/xml/feeds/64/164.xml", 15, 10),
  ("Slashdot",   "http://slashdot.org/slashdot.rdf", 30, 30),
  ("Freshmeat",  "http://freshmeat.net/backend/fm.rdf", 15, 1),
  ("Python News","http://www.python.org/channews.rdf", 60, 30),
  ("CNN News",   "http://www.newsisfree.com/HPE/xml/feeds/96/696.xml.", 15, 10),
  ("BBC News",   "http://www.bbc.co.uk/syndication/feeds/news/ukfs_news/world/rss091.xml", 15, 10)
]

class ContentItem:
	"A channel content class."
	def __init__(s, title, descr, link, date, fromfeed = ""):
		s.title    = title
		s.descr    = descr
		s.link     = link
		s.date     = date
		s.fromfeed = fromfeed
		s.unread   = 1
		s.link_visited = 0

	def show(s, num):
		"Print item info for text interface."
		print "[%2u] %s" % (num, s.get_title())
		if s.descr != "(none)":
			print s.descr
		print "%80s" % s.link

	def get_p_title(s):
		"Return textbox title of item."
		title = entities(stripcontrol(s.title))
		if title == title.upper(): title = title_caps(title)
		return title

	def get_title(s):
		"Return listview title of item. Put in parentheses if already read."
		title = s.get_p_title()
		if s.unread: return title
		else: return "  (" + title + ")"

	def get_s_title(s):
		"Return title of item as seen in search results."
		return s.get_title() + " [" + s.fromfeed + "]"

	def get_date(s):
		"Return the date of the item."
		return s.date

class NewsWire:
	"A channel class that stores its content in s.contents"
	def __init__(s, url = "", name = "", homeurl = "",
			refresh = config['refresh_every'], expire = config['maxtime']):
		if url == "": raise IOError
		s.url        = url
		s.name       = name
		s.descr      = ""
		s.homeurl    = homeurl
		s.refresh    = refresh
		s.expire     = expire
		s.content    = []
		s.headlines  = {}
		s.u_time     = 0		# Time of last update
		s.failed     = 0

	def get_name(s):
		"Return newsfeed name, optionally with number of unread items."
		if s.failed or not s.content: return "  [" + s.name + "]"
		num_unread = s.get_unread()
		if num_unread:
			return s.name + " (" + str(num_unread) + ")"
		else:
			return s.name

	def get_unread(s):
		"Return number of unread items in newsfeed."
		i = 0
		for item in s.content:
			if item.unread: i = i + 1
		return i

	def get_news(s, refresh = 0):
		"Get news items from the Web and decode to instance variables."
		result = {}
		newcontent = []
		if s.content == [] or s.failed or refresh and not s.url == "":
			# Parse the data, returns a dictionary:
			try: result  = rssparser.parse(s.url)
			except (timeoutsocket.Timeout, Exception):
				s.failed = 1
				return 0
			s.failed = 0
			s.title   = result['channel'].get('title', "").strip()
			if s.name[0] == '?' and s.title: s.name = s.title
			s.date    = result['channel'].get('date',
				time.strftime("%Y-%m-%d %H:%M", time.localtime(s.u_time))).strip()
			s.descr   = result['channel'].get('description', s.descr).strip()
			for item in result['items']:
				# Each item is a dictionary mapping properties to values
				title = item.get('title', "(none)")
				descr = item.get('description', "No description available.")
				hash = gethash(title, descr)
				if hash not in s.headlines.keys():
					s.headlines[hash] = s.u_time
					link  = item.get('link', "(none)")
					date  = item.get('date', s.date)
					newcontent.append(ContentItem(title, descr, link,
									date, fromfeed = s.name))
			s.content = newcontent + s.content
			for i in s.headlines.keys():
				if (time.time() - s.headlines[i]) / 86400 > s.expire:
					for j in range(len(s.content) - 1, -1, -1):
						if gethash(s.content[j].title, s.content[j].descr) == i:
							del s.content[j]
							s.headlines[i] = -1
			for i in s.headlines.keys():
				if s.headlines[i] < 0: del s.headlines[i]

		return len(newcontent)

	def print_news(s):
		"Print items to screen and open selected item's URI in browser."
		s.get_news()
		if s.content == []:
			print "\nCurrently no newsfeed. Please try again later."
			return
		print "\n%80s" % s.date
		if s.name != "": print s.name, "--",
		print s.title
		print 78 * "="
		print
		i = 1
		for item in s.content:
			item.show(i)
			i = i + 1
		while 1:
			try:
				topic = input("\nPlease select your topic (\"0\" to go back to menu): ")
			except SyntaxError:
				continue
			if 0 < topic <= len(s.content):
				s.open_news(s.content[topic-1])
			else: break

	def open_news(s, item):
		"Open news item in browser."
		try: webbrowser.open(item.link)
		except webbrowser.Error: print "Error: Opening browser failed."

class SearchWire(NewsWire):
	"A class for searches in newsfeeds."
	def __init__(s, terms, method = "exact", case = 0, words = 0, only_unread = 0):
		s.terms      = terms.strip()
		s.method     = method
		s.case       = case
		s.words      = words
		s.only_unread = only_unread
		if not case: s.terms = string.lower(s.terms)
		s.name       = "Search for '" + s.terms + "'"
		s.content    = []
		s.headlines  = {}
		s.u_time     = approx_time()	# Time of last update
		s.failed     = 0

	def get_news(s, refresh=1):
		"Search for 'terms' in other newsfeeds."
		keepcontent  = []
		newcontent   = []
		oldheadlines = s.headlines
		s.headlines  = {}
		s.u_time     = approx_time()

		if s.words: s.terms = "\\b" + s.terms + "\\b"
		if not s.case: find = re.compile(s.terms, re.IGNORECASE)
		else: find = re.compile(s.terms)
		if s.content == [] or s.failed or refresh:
			for f in newsfeeds:
				if not isinstance(f, SearchWire):
					for t in f.content:
						if find.search(t.title) or find.search(t.descr):
							if not s.only_unread or (s.only_unread and t.unread):
								t.fromfeed = f.name
								newcontent.append(t)
								hash = gethash(t.title, t.descr)
								s.headlines[hash] = f.headlines.get(
										hash, s.u_time)
		if s.only_unread:
			keepcontent = filter(lambda x: not x.unread, s.content)
			for t in keepcontent:
				hash = gethash(t.title, t.descr)
				s.headlines[hash] = oldheadlines.get(hash, s.u_time)
		s.content = keepcontent + newcontent
		return 0

def add_feeds(obj):
	"Accept a list of tuples and add them to the global newsfeed pool."
	global newsfeeds, config
	try: newsfeeds, config = cPickle.load(open(config_file, 'r'))
	except:
		for i in obj:
			try:
				if len(i) > 2: newsfeeds.append(NewsWire(i[1], name=i[0],
							refresh = i[2], expire = i[3]))
				else: newsfeeds.append(NewsWire(i[1], name=i[0]))
			except (IOError, timeoutsocket.Timeout):
				print "Error: Could not find a suitable newsfeed."

def save():
	"Save document cache and configuration options."
	try: cPickle.dump((newsfeeds, config), open(config_file, 'w'))
	except Exception: pass

def quit(event = ""):
	"Exit Program."
	sys.exit(0)

def approx_time():
	"Return an approximate timestamp, so that feeds and stories stay in sync."
	return 10. * int(time.time() / 10)

def plural_s(i):
	"Return an 's' if i > 1."
	if i > 1: return 's'
	return ""

def _by_time_order(x, y):
	"Function for sorting items by download time (or alphabetically if time stamps are equal)."
	a = newsfeeds[app.sel_f].headlines.get(gethash(x.title, x.descr), 0)
	b = newsfeeds[app.sel_f].headlines.get(gethash(y.title, y.descr), 0)

	c = x.title + x.fromfeed
	d = y.title + y.fromfeed

	if a == b:
		if c == d: return 0
		elif c > d: return 1
		else: return -1
	elif a < b: return 1
	else: return -1

def title_caps(t):
	"Do a decent title capitalization."
	words = ["a", "an", "the", "some", "and", "but", "of",
				"on", "or", "nor", "for", "with", "to", "at"]
	t = t.title()
	t = string.replace(t, "'S", "'s")
	for i in words: t = string.replace(t, " %s " % i.title(), " %s " % i)
	return t

def stripcontrol(t):
	"Strip control characters from t."
	subs = (('\r', ''), ('\n', ''))
	for i in subs: t = string.replace(t, i[0], i[1])
	return t

def entities(t):
	"Replace some entities with the symbols they stand for."
	subs = (('&#146;', "'"), ('&amp;', '&'), ('&nbsp;', ' '),
		('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'))
	for i in subs: t = string.replace(t, i[0], i[1])
	for x in range(32, 256):
		xu = "&#%03u;" % x
		t = string.replace(t, xu, chr(x))
 	return t

def htmlrender(t):
	"Transform HTML markup to printable text."
	subs = (('<br>', '\n'), ('</p>', '\n\n'), ('<b>', '*'), ('</b>', '*'),
		('<li>', '\n *'), ('</li>', '\n'),
		('<strong>', '**'), ('</strong>', '**'), ('<em>', '&gt;'), ('</em>', '&lt;'),
		('<u>', '_'), ('</u>', '_'), ('<i>', '~'), ('</i>', '~'),
		('</blockquote>', '\n\n'), ('<img', '[Image]<'))
	for i in subs:
		t = string.replace(t, i[0],         i[1])
		t = string.replace(t, i[0].upper(), i[1])
	return re.sub("<.*?>", "", t)

def gethash(*args):
	"Compute the MD5 hash of the arguments concatenated together."
	h = md5.new()
	for i in args: h.update(i)
	return h.hexdigest()

def text_interface():
	"Present the user with a simple textual interface to the RSS feeds."
	if newsfeeds:
		while 1:
			print "\nAvailable newsfeeds:\n"
			for i in range(len(newsfeeds)):
				print "[%2u] %s" % (i+1, newsfeeds[i].get_name())
			try:
				feed = input("\nPlease select your feed (\"0\" to quit): ")
			except SyntaxError: continue
			if 0 < feed <= len(newsfeeds):
				try:
					newsfeeds[feed-1].print_news()
				except timeoutsocket.Timeout:
					print "Operation timed out. ",
					print "Please choose a different feed..."
			else: quit()

class TkApp:
	"GUI class for use with the Tk interface."
	def __init__(s, parent):
		s.sel_f  = -1
		s.sel_t  = -1
		s.parent = parent
		s.refresh_feeds     = []		# Feeds to update
		s.num_refresh_feeds = 0 		# Number of feeds to update
		s.refresh_now       = 0
		s.num_empty_feeds   = 0
		s.idle_since        = time.time()
		s.total_unread      = 0

		s.infowin   = ""
		s.searchwin = ""

		# Frames:
		f1 = Frame(parent)
		f1.pack(side = TOP, expand = 0, fill = X)
		f2 = Frame(parent)
		f2.pack(side = BOTTOM, expand = 1, fill = BOTH)
		f3 = Frame(f1)
		f3.pack(side = LEFT, expand = 1, fill = BOTH)
		f4 = Frame(f1)
		f4.pack(side = RIGHT, expand = 1, fill = BOTH)
		f5 = Frame(f2)
		f5.pack(side = LEFT, expand = 0, fill = Y)
		f6 = Frame(f2)
		f6.pack(side = RIGHT, expand = 1, fill = BOTH)
		f7 = Frame(f6)
		f7.pack(side = TOP, expand = 1, fill = BOTH)
		f8 = Frame(f6)
		f8.pack(side = BOTTOM, expand = 1, fill = BOTH)

		# Buttons:
		s.b_refresh = Button(f3, text = "Refresh Now", command = s.refresh)
		s.b_refresh.pack(side = LEFT)
		s.b_info = Button(f3, text = "Edit Channel", command = s.info)
		s.b_info.pack(side = LEFT)
		s.b_sub = Button(f3, text = "Subscribe", command = s.sub)
		s.b_sub.pack(side = LEFT)
		s.b_unsub = Button(f3, text = "Unsubscribe", command = s.unsub)
		s.b_unsub.pack(side = LEFT)
		s.b_search = Button(f3, text = "Search News", command = s.new_search)
		s.b_search.pack(side = LEFT)

		s.b_delall = Button(f4, text = "Delete All", command = s.delete_all_in_feed)
		s.b_delall.pack(side = RIGHT)
		s.b_del = Button(f4, text = "Delete", command = s.delete_one)
		s.b_del.pack(side = RIGHT)
		s.b_allread = Button(f4, text = "Mark All As Read", command = s.mark_all_as_read)
		s.b_allread.pack(side = RIGHT)
		s.b_next = Button(f4, text = "Next Unread", command = s.next)
		s.b_next.pack(side = RIGHT)

		# Listboxes and Text widget:
		f9 = Frame(f5)
		f9.pack(side = BOTTOM, fill = BOTH)
		s.b_cancel = Button(f9, text = "X", command = s.cancel_update, state = DISABLED)
		s.b_cancel.pack(side = RIGHT)
		s.pbar = Canvas(f9, width = 120, height = 24)
		s.pbar.pack(side = TOP, fill = BOTH)
		s.pbar.create_rectangle(0, 4, 150, 22, fill = "white")
		s.pbarline = s.pbar.create_rectangle(0, 4, 0, 22, fill = "#009b2e")

		f_ud = Frame(f5)
		f_ud.pack(side = BOTTOM, expand = 0, fill = X)
		f_ud1 = Frame(f_ud)
		f_ud1.pack(side = LEFT, expand = 1, fill = X)
		f_ud2 = Frame(f_ud)
		f_ud2.pack(side = RIGHT, expand = 1, fill = X)
		s.b_up = Button(f_ud1, text = "Move Up", command = s.up)
		s.b_up.pack(side = LEFT, expand = 1, fill = X)
		s.b_dn = Button(f_ud2, text = "Move Down", command = s.down)
		s.b_dn.pack(side = RIGHT, expand = 1, fill = X)

		s.lb_scr = Scrollbar(f5)
		s.lb_scr.pack(side = RIGHT, fill = Y)
		s.lb = Listbox(f5, width = 24, selectmode = SINGLE, yscrollcommand = s.lb_scr.set)
		for i in newsfeeds:
			s.lb.insert(END, i.get_name())
		s.lb.config(background = "#96c8ff", selectforeground = "white",
							selectbackground = "#3d9aff")
		s.lb.pack(side = TOP, expand = 1, fill = BOTH)
		s.lb_scr.config(command = s.lb.yview)

		s.r1b_scr = Scrollbar(f7)
		s.r1b_scr.pack(side = RIGHT, fill = Y)
		s.r11b = Listbox(f7, selectmode = SINGLE, width = 30, yscrollcommand = s.r1b_scr.set)
		for i in newsfeeds[0].content:
			s.r11b.insert(END, i.date)
		s.r11b.config(background = "#ffefaf", selectforeground = "white",
							selectbackground = "#ffc054")
		s.r11b.pack(side = RIGHT, expand = 0, fill = BOTH)

		s.r1b = Listbox(f7, selectmode = SINGLE, yscrollcommand = s.r1b_scr.set)
		for i in newsfeeds[0].content:
			s.r1b.insert(END, i.get_title())
		s.r1b.config(background = "#ffefaf", selectforeground = "white",
							selectbackground = "#ffc054")
		s.r1b.pack(side = TOP, expand = 1, fill = BOTH)
		s.r1b_scr.config(command = s._yview)

		s.r2b_scr = Scrollbar(f8)
		s.r2b_scr.pack(side = RIGHT, fill = Y)
		s.r2b = Text(f8, wrap = WORD, cursor = "", yscrollcommand = s.r2b_scr.set)
		s.r2b.config(state = DISABLED, background = "#fffbea",
				selectforeground = "white", selectbackground ="#233a8e")
		s.r2b.pack(side = BOTTOM, expand = 1, fill = BOTH)
		s.r2b_scr.config(command = s.r2b.yview)

		s.parent.bind("<space>", s.next)
		s.parent.bind("s", s.new_search)
		s.parent.bind("r", s.refresh)
		s.parent.bind("e", s.info)
		s.parent.bind("i", s.iconify)
		s.parent.bind("m", s.mark_all_as_read)
		s.parent.bind("<Return>", s.open)
		s.parent.bind("o", s.open)
		s.parent.bind("<BackSpace>", s.delete_one)
		s.parent.bind("d", s.delete_one)
		s.parent.bind("<Escape>", s.cancel_update)
		s.parent.bind("q", quit)
		s.parent.bind("<Prior>", s.page_up)
		s.parent.bind("<Next>", s.page_down)
		s.parent.bind("<Up>", s.line_up)
		s.parent.bind("<Down>", s.line_down)
		s.parent.bind("<End>", s.last_page)
		s.parent.bind("<Home>", s.first_page)
		s.parent.focus()

		parent.after(250, s.beat)

	def iconify(s, event = ""):
		"Iconify the application."
		s.parent.iconify()

	def _yview(s, *args):
		"Update the message header and date listbox in unison."
		apply(s.r11b.yview, args)
		apply(s.r1b.yview, args)

	def line_down(s, event = ""):
		"Scroll text widget down one line."
		s.r2b.yview(SCROLL, 1, UNITS)

	def line_up(s, event = ""):
		"Scroll text widget up one line."
		s.r2b.yview(SCROLL, -1, UNITS)

	def page_down(s, event = ""):
		"Scroll text widget down one page."
		s.r2b.yview(SCROLL, 1, PAGES)

	def page_up(s, event = ""):
		"Scroll text widget up one page."
		s.r2b.yview(SCROLL, -1, PAGES)

	def last_page(s, event = ""):
		"Go to last page of text."
		s.r2b.yview(MOVETO, 1.0)

	def first_page(s, event = ""):
		"Go to first page of text."
		s.r2b.yview(MOVETO, 0.0)

	def progress(s):
		"Return the current progress value in percent."
		try: return 100 - 100 * (len(s.refresh_feeds) - 1) / s.num_refresh_feeds
		except ZeroDivisionError: return 0

	def draw_bar(s, p):
		"Draw a progress bar while updating the feeds."
		if p > 100 or p < 0: p = 0
		s.pbar.coords(s.pbarline, 1, 4, int(1.5 * p), 22)

	def _update_feed_list(s):
		"Update the list of feeds."
		s.lb.delete(0, END)
		for i in newsfeeds:
			feedname = s._active(i.get_name(), i, newsfeeds[s.sel_f])
			s.lb.insert(END, feedname)

	def _window_title(s, feed):
		"Update the Root window title."
		title = "%s - %s" % (newsfeeds[feed].name, config['progname'])
		i = 0
		j = 0
		for f in newsfeeds:
			if not isinstance(f, SearchWire):
				num_unread = f.get_unread()
				i = i + num_unread
				if num_unread: j = j + 1
		if i:
			title = "%s (%u unread item%s in %u channel%s)" % (
						title, i, plural_s(i), j, plural_s(j))
			iconname = "%u unread" % i
		else: iconname = config['progname']
		s.parent.title(title)
		if s.refresh_feeds: iconname = "%u (%2u%%)" % (i, s.progress())
		s.parent.iconname(iconname)

		# Play notification sound if there are new unread messages:
		if not s.total_unread and i:
			try: sound.play(blocking = 1)
			except (TclError, Exception): pass
		s.total_unread = i

	def _active(s, str, a, b):
		"Return an 'active' marker if a == b."
		if a == b: return str.upper()
		return str

	def change_content(s, feed = 0, topic = 0):
		"Switch to a different content item."
		feed = int(feed)
		topic = int(topic)
		if feed >= len(newsfeeds): feed = len(newsfeeds) - 1
		if feed < 0: feed = 0
		newsfeeds[feed].get_news()
		if topic >= len(newsfeeds[feed].content): topic = len(newsfeeds[feed].content) - 1
		if topic < 0: topic = 0
		if feed != s.sel_f: s.sel_t = 0
		else: s.sel_t = topic
		s.sel_f = feed

		if isinstance(newsfeeds[s.sel_f], SearchWire):
			s.b_info.config(state = DISABLED)
			sortcontent = newsfeeds[s.sel_f].content
			sortcontent.sort(_by_time_order)
			if sortcontent:
				sortcontent[s.sel_t].unread = 0
				item = sortcontent[s.sel_t]
				hash = gethash(item.title, item.descr)
				for f in newsfeeds:
					if f is not newsfeeds[s.sel_f]:
						for t in filter(lambda x: gethash(
							x.title, x.descr) == hash, f.content):
							t.unread = 0
			items = [x.get_s_title() for x in sortcontent]
		else:
			if s.b_info.cget("state") == "disabled": s.b_info.config(state = NORMAL)
			if newsfeeds[s.sel_f].content: newsfeeds[s.sel_f].content[s.sel_t].unread = 0
			items = [x.get_title() for x in newsfeeds[s.sel_f].content]

		s._change_text(s.r2b)
		s._change_list(s.r1b, items, s.sel_t)
		s._change_list(s.r11b, [x.get_date() for x in newsfeeds[s.sel_f].content], s.sel_t)
		s._change_list(s.lb, [x.get_name() for x in newsfeeds], s.sel_f)
		s._window_title(s.sel_f)

	def _show_hand_cursor(s, event = ""):
		"Show a hand cursor (for links)."
		s.r2b.config(cursor = "hand2")

	def _show_pointer_cursor(s, event = ""):
		"Revert to normal cursor."
		s.r2b.config(cursor = "")

	def _change_text(s, obj):
		"Change textbox."
		obj.config(state = NORMAL)
		obj.delete(1.0, END)
		obj.config(state = DISABLED)
		if not newsfeeds[s.sel_f].content: return

		obj.config(state = NORMAL)
		obj.tag_config("DATE", foreground = "#00059e", justify = RIGHT, font = ("Courier", 12))
		obj.tag_config("DLDATE", foreground = "#00059e", justify = RIGHT, font = ("Courier", 12))
		if newsfeeds[s.sel_f].content[s.sel_t].link_visited:
			obj.tag_config("HEADLINE", foreground = "#9600b5", underline = 1,
									 font = ("Times", 20))
		else: obj.tag_config("HEADLINE", foreground = "blue", underline = 1, font = ("Times", 20))
		obj.tag_bind("HEADLINE", "<ButtonRelease-1>", s.open)
		obj.tag_bind("HEADLINE", "<ButtonRelease-2>", s.open)
		obj.tag_bind("HEADLINE", "<Enter>", s._show_hand_cursor)
		obj.tag_bind("HEADLINE", "<Leave>", s._show_pointer_cursor)
		obj.tag_config("DESCR", spacing2 = 5, font = ("Times", 16))
		obj.tag_config("URL", foreground = "#ff2600", justify = RIGHT, font = ("Courier", 12))

		story = newsfeeds[s.sel_f].content[s.sel_t]

		obj.insert(END, story.date + "\n\n", ("DATE"))
		obj.insert(END, story.get_p_title(), ("HEADLINE"))
		obj.insert(END, "\n\n" + entities(htmlrender(stripcontrol(
								story.descr))) + "\n\n", ("DESCR"))
		obj.insert(END, story.link + "\n\n", ("URL"))
		obj.insert(END, time.strftime("%Y-%m-%d %H:%M",
			time.localtime(newsfeeds[s.sel_f].headlines[gethash(story.title, story.descr)])),
											("DLDATE"))
		obj.config(state = DISABLED)

	def _change_list(s, obj, list, selnum):
		"Change one of the listboxes."
		a, b = [int(.5 + len(list) * x) for x in obj.yview()]
		b -= 1

                obj.delete(0, END)
		if not list: return

		for i in range(len(list)): obj.insert(END, s._active(list[i], i, selnum))

		if selnum:
			if selnum < a or selnum > b: obj.see(selnum)
			else: obj.yview(a)

		obj.select_clear(0, END)
		if obj is s.r1b: obj.select_set(selnum)
		
	def next(s, event = ""):
		"Jump to next unread item."
		t = s._next_in_feed(feed = s.sel_f, topic = s.sel_t)
		if t:
			s.change_content(feed = s.sel_f, topic = t - 1)
			return
		for f in range(s.sel_f, len(newsfeeds)):
			t = s._next_in_feed(feed = f)
			if t:
				s.change_content(feed = f, topic = t - 1)
				return
		for f in range(0, s.sel_f):
			t = s._next_in_feed(feed = f)
			if t:
				s.change_content(feed = f, topic = t - 1)
				return

	def _next_in_feed(s, feed = 0, topic = 0):
		"Find next unread message in feed 'feed', starting from topic 'topic'."
		for i in range(topic, len(newsfeeds[feed].content)):
			if newsfeeds[feed].content[i].unread:
				return i + 1
		for i in range(0, topic):
			if newsfeeds[feed].content[i].unread:
				return i + 1
		return 0

	def mark_all_as_read(s, event = ""):
		"Mark all items in current channel as read."
		for i in newsfeeds[s.sel_f].content:
			i.unread = 0
		s.change_content(feed = s.sel_f)

	def delete_one(s, event = ""):
		"Delete one entry (and remember not to download it again)."
		t = newsfeeds[s.sel_f].content[s.sel_t]
		hash = gethash(t.title, t.descr)
		if isinstance(newsfeeds[s.sel_f], SearchWire):
			for f in newsfeeds:
				if f is not newsfeeds[s.sel_f]:
					f.content = filter(lambda x: gethash(
								x.title, x.descr) != hash, f.content)
		del newsfeeds[s.sel_f].content[s.sel_t]
		s.change_content(feed = s.sel_f, topic = s.sel_t)
		s._update_searches()

	def delete_all_in_feed(s):
		"Delete all items in current feed as well as copies in other feeds and then refresh view."
		if isinstance(newsfeeds[s.sel_f], SearchWire):
			for t in newsfeeds[s.sel_f].content:
				hash = gethash(t.title, t.descr)
				for f in newsfeeds:
					if f is not newsfeeds[s.sel_f]:
						f.content = filter(lambda x: gethash(
							x.title, x.descr) != hash, f.content)
						if f.headlines.has_key(hash): del f.headlines[hash]
		newsfeeds[s.sel_f].content   = []
		newsfeeds[s.sel_f].headlines.clear()
		s.change_content(feed = s.sel_f)

	def open(s, event = ""):
		"Open news item link in web browser."
		if not newsfeeds[s.sel_f].content: return
		newsfeeds[s.sel_f].content[s.sel_t].link_visited = 1
		newsfeeds[s.sel_f].open_news(newsfeeds[s.sel_f].content[s.sel_t])
		s.change_content(feed = s.sel_f, topic = s.sel_t)

	def refresh(s, event = ""):
		"Refresh all newsfeeds."
		if s.refresh_now < 1:
			s.refresh_now = 1

	def cancel_update(s, event = ""):
		"Cancel an update in progress."
		s.refresh_feeds = []
		s.change_content(feed = s.sel_f, topic = s.sel_t)

	def discover(s):
		"Try to discover RSS feed for given site."
		rss = ""
		try: rss = rssfinder.getFeeds(s.e2.get())
		except (IOError, timeoutsocket.Timeout, Exception): pass
		else:
			if len(rss) > 1:
				newcontent = []
				for i in range(len(rss)):
					newcontent.insert(0, NewsWire(
						name = "? #%u (%s)" % (i + 1, s.e2.get()),
									url = rss[i]))
				for i in newcontent: newsfeeds.insert(s.sel_f + 1, i)
			elif rss:
				newsfeeds[s.sel_f].url = rss[0]
				s.e3.delete(0, END)
				s.e3.insert(END, newsfeeds[s.sel_f].url)
			else:
				s.e3.delete(0, END)
				s.e3.insert(END, "Unable to locate feed for site " + s.e2.get())
		
	def _is_window_open(s, w):
		"Is the window 'w' already open? If so, raise it."
		try: tmp = w.geometry()
		except (TclError, Exception): return 0
		else:
			w.lift()
			w.focus()
			return 1

	def info(s, event = ""):
		"Display editable info about current channel."
		if isinstance(newsfeeds[s.sel_f], SearchWire): return
		if s._is_window_open(s.infowin): return

		s.infowin = Toplevel()
		s.infosel = s.sel_f
		s.infowin.title("Subscription Info")
		s.infowin.geometry(config['geom_info'])

		f1 = Frame(s.infowin, borderwidth = 10)
		f1.pack(side = TOP)
		f2 = Frame(f1)
		f2.pack(side = LEFT)
		l1 = Label(f2, text = "Name:")
		l1.pack()
		f3 = Frame(f1)
		f3.pack(side = RIGHT)
		s.e1 = Entry(f3, width = 65)
		s.e1.insert(END, newsfeeds[s.sel_f].name)
		s.e1.pack(side = LEFT)

		f4 = Frame(s.infowin, borderwidth = 10)
		f4.pack(side = TOP)
		f5 = Frame(f4)
		f5.pack(side = LEFT)
		l2 = Label(f5, text = "Home:")
		l2.pack()
		f6 = Frame(f4)
		f6.pack(side = RIGHT)
		s.e2 = Entry(f6, width = 65)
		s.e2.insert(END, newsfeeds[s.sel_f].homeurl)
		s.e2.pack(side = LEFT)

		f7 = Frame(s.infowin, borderwidth = 10)
		f7.pack(side = TOP)
		f8 = Frame(f7)
		f8.pack(side = LEFT)
		l3 = Label(f8, text = "  RSS:")
		l3.pack()
		f9 = Frame(f7)
		f9.pack(side = RIGHT)
		s.e3 = Entry(f9, width = 65)
		s.e3.insert(END, newsfeeds[s.sel_f].url)
		s.e3.pack(side = LEFT)

		f14 = Frame(s.infowin)
		f14.pack(side = TOP, padx = 90, pady = 10, fill = X)
		f15 = Frame(f14)
		f15.pack(side = LEFT)
		f16 = Frame(f14)
		f16.pack(side = RIGHT)
		f17 = Frame(f15)
		f17.pack(side = LEFT)
		f18 = Frame(f15)
		f18.pack(side = RIGHT)
		f19 = Frame(f16)
		f19.pack(side = LEFT)
		f20 = Frame(f16)
		f20.pack(side = RIGHT)
		l4 = Label(f17, text = "Update every:")
		l4.pack(side = RIGHT)
		s.o1var = StringVar()
		if newsfeeds[s.sel_f].refresh == 5: s.o1var.set("5 minutes")
		elif newsfeeds[s.sel_f].refresh == 15: s.o1var.set("15 minutes")
		elif newsfeeds[s.sel_f].refresh == 30: s.o1var.set("30 minutes")
		else: s.o1var.set("60 minutes")
		o1 = OptionMenu(f18, s.o1var, "5 minutes", "15 minutes", "30 minutes", "60 minutes")
		o1.config(width = 11)
		o1.pack(side = LEFT)
		l5 = Label(f19, text = "Expire after:")
		l5.pack(side = RIGHT)
		s.o2var = StringVar()
		if newsfeeds[s.sel_f].expire == 1: s.o2var.set("1 day")
		elif newsfeeds[s.sel_f].expire == 10: s.o2var.set("10 days")
		elif newsfeeds[s.sel_f].expire == 30: s.o2var.set("30 days")
		else: s.o2var.set("Never")
		o2 = OptionMenu(f20, s.o2var, "1 day", "10 days", "30 days" , "Never")
		o2.config(width = 8)
		o2.pack(side = LEFT)

		f10 = Frame(s.infowin)
		f10.pack(side = TOP, pady = 20)
		f11 = Frame(f10)
		f11.pack(side = LEFT)
		f12 = Frame(f10, width = 120)
		f12.pack(side = LEFT)
		f13 = Frame(f10)
		f13.pack(side = LEFT)
		b1 = Button(f11, text = "Auto-Detect RSS Feed", command = s.discover)
		b1.pack(side = LEFT)
		b2 = Button(f13, text = "Save Information", command = s._update)
		b2.pack(side = RIGHT)

		# Add site description:
		f14 = Frame(s.infowin)
		f14.pack(side = TOP, padx = 50)
		s.t_descr = Text(f14, wrap = WORD, width = 60, height = 8)
		s.t_descr.insert(END, newsfeeds[s.sel_f].descr)
		s.t_descr.config(state = DISABLED, background = "#fffbea",
					selectforeground = "white", selectbackground ="#233a8e")
		s.t_descr.pack(side = BOTTOM, expand = 1, fill = BOTH)
		s.e1.bind("<Return>", s._update)
		s.e3.bind("<Return>", s._update)
		s.e1.focus()

	def _update(s, event = ""):
		"Update the channel information."
		if not s.e1.get().strip() or not s.e3.get().strip(): return
		newsfeeds[s.infosel].name    = s.e1.get().strip()
		newsfeeds[s.infosel].homeurl = s.e2.get().strip()
		newsfeeds[s.infosel].url     = s.e3.get().strip()

		refresh = s.o1var.get()
		newsfeeds[s.infosel].refresh = int(string.split(refresh)[0])

		expire  = s.o2var.get()
		try: newsfeeds[s.infosel].expire  = int(string.split(expire)[0])
		except ValueError: newsfeeds[s.infosel].expire = 999999
		
		config['geom_info'] = s.infowin.geometry()
		s.infowin.destroy()
		s.change_content(feed = s.sel_f)

	def sub(s):
		"Subscribe to new channel."
		newsfeeds.insert(s.sel_f + 1, NewsWire(name = "New Channel", url = "http://"))
		s.change_content(feed = s.sel_f + 1)
		s.info()

	def unsub(s):
		"Remove current channel."
		if s.refresh_now: return
		if len(newsfeeds) == 1: return
		del newsfeeds[s.sel_f]
		s._update_searches()
		s.change_content(feed = s.sel_f)

	def new_search(s, event = ""):
		"Create a new search entry."
		if s._is_window_open(s.searchwin): return
		s.searchwin = Toplevel()
		s.searchwin.title("Create New Search")
		s.searchwin.geometry(config['geom_search'])

		f1 = Frame(s.searchwin)
		f1.pack(side = TOP)
		f2 = Frame(f1)
		f2.pack(side = LEFT)
		f3 = Frame(f1)
		f3.pack(side = RIGHT)
		l_search = Label(f2, text = "Search for:")
		l_search.pack(side = TOP)
		s.e_search = Entry(f3)
		s.e_search.pack(side = TOP, pady = 20)

		f4 = Frame(s.searchwin)
		f4.pack(side = TOP, fill = X, padx = 40)
		s.search_is_case_sensitive = IntVar()
		s.search_is_case_sensitive.set(config['search_is_case_sensitive'])
		s.c_search_case = Checkbutton(f4, text = "Match Case",
						variable = s.search_is_case_sensitive)
		s.c_search_case.pack(side = LEFT)

		f5 = Frame(s.searchwin)
		f5.pack(side = TOP, fill = X, padx = 40)
		s.search_match_whole_words = IntVar()
		s.search_match_whole_words.set(config['search_match_whole_words'])
		s.c_search_words = Checkbutton(f5, text = "Match Whole Words",
						variable = s.search_match_whole_words)
		s.c_search_words.pack(side = LEFT)

		f6 = Frame(s.searchwin)
		f6.pack(side = TOP, fill = X, padx = 40)
		s.search_only_unread = IntVar()
		s.search_only_unread.set(config['search_only_unread'])
		s.c_search_only_unread = Checkbutton(f6, text = "Search Only in Unread Items",
						variable = s.search_only_unread)
		s.c_search_only_unread.pack(side = LEFT)

		s.b_search = Button(s.searchwin, text = "Accept", command = s._new_search_finished)
		s.b_search.pack(side = TOP, pady = 20)
		s.e_search.bind("<Return>", s._new_search_finished)
		s.e_search.focus()

	def _new_search_finished(s, event = ""):
		"Accept the user's search."
		case  = int(s.search_is_case_sensitive.get())
		words = int(s.search_match_whole_words.get())
		only_unread = int(s.search_only_unread.get())
		newsfeeds.insert(s.sel_f + 1, SearchWire(s.e_search.get().strip(), case = case,
							words = words, only_unread = only_unread))
		config['search_is_case_sensitive'] = case
		config['search_match_whole_words'] = words
		config['search_only_unread']       = only_unread
		s.change_content(feed = s.sel_f + 1)
		config['geom_search'] = s.searchwin.geometry()
		s.searchwin.destroy()
		s._update_searches()

	def _update_searches(s):
		"Update all search feeds."
		for i in newsfeeds:
			if isinstance(i, SearchWire):
				s.refresh_feeds.append(i)
				s.num_refresh_feeds += 1
				s.draw_bar(s.progress())

	def up(s):
		"Move a channel up in list."
		if s.refresh_now: return
		if s.sel_f:
			newsfeeds[s.sel_f], newsfeeds[s.sel_f - 1] = newsfeeds[
							s.sel_f - 1], newsfeeds[s.sel_f]
			s.change_content(feed = s.sel_f - 1)

	def down(s):
		"Move a channel down in list."
		if s.refresh_now: return
		if s.sel_f < len(newsfeeds) - 1:
			newsfeeds[s.sel_f], newsfeeds[s.sel_f + 1] = newsfeeds[
							s.sel_f + 1], newsfeeds[s.sel_f]
			s.change_content(feed = s.sel_f + 1)

	def beat(s):
		"Look if any updating of feeds is necessary."
		if len(s.lb.curselection())  and int(s.lb.curselection()[0])  != s.sel_f:
			s.idle_since = time.time()
			s.change_content(feed = s.lb.curselection()[0])
		if len(s.r1b.curselection()) and int(s.r1b.curselection()[0]) != s.sel_t:
			s.idle_since = time.time()
			s.change_content(feed = s.sel_f, topic = s.r1b.curselection()[0])
		if len(s.r11b.curselection()) and int(s.r11b.curselection()[0]) != s.sel_t:
			s.idle_since = time.time()
			s.change_content(feed = s.sel_f, topic = s.r11b.curselection()[0])

		# Look for changes in the number of empty feeds:
		num_empty_feeds = len(filter(lambda x: x.content == [], newsfeeds))
		if num_empty_feeds != s.num_empty_feeds: s._update_searches()
		s.num_empty_feeds = num_empty_feeds

		# First stage of global refresh. Add all feeds to array of feeds to be reloaded:
		if s.refresh_now == 1:
			newsfeeds[s.sel_f].u_time = approx_time()
			s.refresh_feeds.append(newsfeeds[s.sel_f])
			for i in newsfeeds:
				if i is not newsfeeds[s.sel_f] and not isinstance(i, SearchWire):
					s.refresh_feeds.append(i)
					i.u_time = newsfeeds[s.sel_f].u_time
			for i in newsfeeds:
				if isinstance(i, SearchWire): s.refresh_feeds.append(i)
			s.num_refresh_feeds += len(newsfeeds)
			s.refresh_now = 2

		# Second stage, do the actual downloading:
		if s.refresh_feeds:
			for b in s.b_refresh, s.b_unsub, s.b_allread, s.b_up, s.b_dn:
				b.config(state = DISABLED)
			if s.b_cancel.cget("state") == "disabled":
				s.b_cancel.config(state = NORMAL)
			s.draw_bar(s.progress())
			if s.refresh_feeds[0] is newsfeeds[s.sel_f]:
				s.change_content(feed = s.sel_f,
					topic = s.sel_t + s.refresh_feeds.pop(0).get_news(refresh = 1))
			else: s.refresh_feeds.pop(0).get_news(refresh = 1)
			s.change_content(feed = s.sel_f, topic = s.sel_t)
		else:
			for b in s.b_refresh, s.b_unsub, s.b_allread, s.b_up, s.b_dn:
				if b.cget("state") == "disabled":
					b.config(state = NORMAL)
			s.b_cancel.config(state = DISABLED)
			s.refresh_now = 0
			s.num_refresh_feeds = 0
			s.draw_bar(0)

		# Look for feeds that require updating:
		some_feeds_need_updating = 0
		new_time = approx_time()
		for i in newsfeeds:
			if not isinstance(i, SearchWire):
				if (time.time() - i.u_time) / 60 > i.refresh:
					some_feeds_need_updating = 1
					i.u_time = new_time
					s.refresh_feeds.append(i)
					s.num_refresh_feeds += 1
					s.draw_bar(s.progress())

		# Also update the searches if one or more feeds need to be updated:
		if some_feeds_need_updating: s._update_searches()

		config['geom_root'] = s.parent.geometry()

		# This reduction of interactivity is done to limit Tkinter memory leakage:
		if time.time() - s.idle_since > 60 and not s.refresh_feeds:
			s.parent.after(1000, s.beat)
		elif time.time() - s.idle_since > 10 and not s.refresh_feeds:
			s.parent.after(200, s.beat)
		else: s.parent.after(50, s.beat)

class dummysound:
	"Use this if Snack is unavailable."
	def play(s): pass

def gui_interface():
	"Tk interface routine."
	global app, sound

	root = Tk()

	root.title(config['progname'] + " -- " + newsfeeds[0].name)
	root.geometry(config['geom_root'])

	if tkSnack != None:
		tkSnack.initializeSnack(root)
		sound = tkSnack.Sound(load = soundfile)
	else: sound = dummysound()

	app = TkApp(root)
	app.change_content()
	root.protocol("WM_DELETE_WINDOW", quit)
	root.iconname(config['progname'])

	root.mainloop()

def main():
	"Main Program. Start either textual or graphical interface."
	add_feeds(initial)
	if config['mode'] == "text": text_interface()
	else: gui_interface()

if __name__ == '__main__':
	try: main()
	finally: save()