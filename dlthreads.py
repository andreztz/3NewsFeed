"""
Module that sets up download processes

2011-01-03
"""

import sys, socket, urllib.request, urllib.error, urllib.parse
socket.setdefaulttimeout(20)

from multiprocessing import Queue, Process
from queue import Empty, Full
import feedparser

def worker():
	while True:
		try: isweb, d = urlq.get()
		except: pass
		if isweb:
			try:
				result = get_content_unicode(d[0])
			except:
				result = "failed"
		else:
			try:
				# Parse data, return a dictionary:
				result = feedparser.parse(d[0],
						etag = d[1],
						modified = d[2])
				result['bozo_exception'] = ''
			except:
				result = "failed"
		urlr.put((d[0], result))

def get_content_unicode(url):
	"Get the URL content and convert to Unicode."
	ugen = urllib.request.urlopen(url)
	rawhtml = ugen.read()
	content_type = 'iso-8859-1'
	th = ugen.info().typeheader
	if 'charset' in th:
		content_type = th.split('=')[-1]
	elif 'charset=' in rawhtml:
		for x in rawhtml.splitlines(1):
			try:
				c = re.compile('charset=(.+)"').search(x).expand("\g<0>")
				content_type = c.split('=')[-1][0:-1]
			except: pass
			else: break
	try: rawhtml = rawhtml.decode(content_type)
	except:
		sys.stderr.write("*** Warning: Encoding %s not supported by Python, defaulting to iso-8859-1.\n"
					% content_type)
		rawhtml = rawhtml.decode('iso-8859-1')
	return rawhtml

def start():
	global num_worker_threads, urlq, urlr, new_data, program_run, ti
	num_w = 4		# number of download processes
	urlq = Queue()		# query queue
	urlr = Queue()		# result queue

	for i in range(num_w):
		ti = Process(target=worker)
		ti.daemon = True
		ti.start()
