"""Ultra-liberal feed finder

http://diveintomark.org/projects/feed_finder/

Usage:
getFeeds(uri) - returns list of feeds associated with this address

Example:
>>> import feedfinder
>>> feedfinder.getFeeds('http://diveintomark.org/')
['http://diveintomark.org/xml/atom.xml']
>>> feedfinder.getFeeds('macnn.com')
['http://www.macnn.com/macnn.rdf']

Can also use from the command line.  Feeds are returned one per line:
$ python feedfinder.py diveintomark.org
http://diveintomark.org/xml/atom.xml

How it works:
0. At every step, feeds are minimally verified to make sure they are really feeds.
1. If the URI points to a feed, it is simply returned; otherwise
   the page is downloaded and the real fun begins.
2. Feeds pointed to by LINK tags in the header of the page (autodiscovery)
3. <A> links to feeds on the same server ending in ".rss", ".rdf", ".xml", or ".atom"
4. <A> links to feeds on the same server containing "rss", "rdf", "xml", or "atom"
5. <A> links to feeds on external servers ending in ".rss", ".rdf", ".xml", or ".atom"
6. <A> links to feeds on external servers containing "rss", "rdf", "xml", or "atom"
7. As a last ditch effort, we search Syndic8 for feeds matching the URI

"""

__version__ = "1.2"
__date__ = "2004-01-09"
__author__ = "Mark Pilgrim (f8dy@diveintomark.org)"
__copyright__ = "Copyright 2002-4, Mark Pilgrim"
__license__ = "Python"
__credits__ = """Abe Fettig for a patch to sort Syndic8 feeds by popularity
Also Jason Diamond, Brian Lalor for bug reporting and patches"""
__history__ = """
1.1 - MAP - 2003/02/20 - added support for Robot Exclusion Standard.  Will
fetch /robots.txt once per domain and verify that URLs are allowed to be
downloaded.  Identifies itself as
  rssfinder/<version> Python-urllib/<version> +http://diveintomark.org/projects/rss_finder/
1.2 - MAP - 2004-01-09 - added Atom support, changed name, relicensed,
  don't query Syndic8 by default (pass querySyndic8=1 to getFeeds to do it anyway)
"""

_debug = 0

# ---------- required modules (should come with any Python distribution) ----------
import sgmllib3, urllib.request, urllib.parse, urllib.error, urllib.parse, re, sys

# ---------- optional modules (feedfinder will work without these, but with reduced functionality) ----------

# timeoutsocket allows feedfinder to time out rather than hang forever on ultra-slow servers.
# Python 2.3 now has this functionality available in the standard socket library, so under
# 2.3 you don't need to install anything.
import socket
if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(10)
else:
    try:
        import timeoutsocket # http://www.timo-tasi.org/python/timeoutsocket.py
        timeoutsocket.setDefaultSocketTimeout(10)
    except ImportError:
        pass

# XML-RPC support allows feedfinder to query Syndic8 for possible matches.
# Python 2.3 now comes with this module by default, otherwise you can download it
try:
    import xmlrpc.client # http://www.pythonware.com/products/xmlrpc/
except ImportError:
    xmlrpclib = None

if not dict:
    def dict(aList):
        rc = {}
        for k, v in aList:
            rc[k] = v
        return rc
    
def _debuglog(message):
    if _debug: print(message)

class BaseParser(sgmllib3.SGMLParser):
    def __init__(self, baseuri):
        sgmllib3.SGMLParser.__init__(self)
        self.links = []
        self.baseuri = baseuri
        
    def normalize_attrs(self, attrs):
        attrs = [(k.lower(), sgmllib3.charref.sub(lambda m: chr(int(m.groups()[0])), v).strip()) for k, v in attrs]
        attrs = [(k, k in ('rel','type') and v.lower() or v) for k, v in attrs]
        return attrs
        
    def do_base(self, attrs):
        attrsD = dict(self.normalize_attrs(attrs))
        if 'href' not in attrsD: return
        self.baseuri = attrsD['href']
        
class LinkParser(BaseParser):
    FEED_TYPES = ('application/rss+xml',
                  'text/xml',
                  'application/atom+xml',
                  'application/x.atom+xml',
                  'application/x-atom+xml')
    def do_link(self, attrs):
        attrsD = dict(self.normalize_attrs(attrs))
        if 'rel' not in attrsD: return
        rels = attrsD['rel'].split()
        if 'alternate' not in rels: return
        if attrsD.get('type') not in self.FEED_TYPES: return
        if 'href' not in attrsD: return
        self.links.append(urllib.parse.urljoin(self.baseuri, attrsD['href']))

class ALinkParser(BaseParser):
    def start_a(self, attrs):
        attrsD = dict(self.normalize_attrs(attrs))
        if 'href' not in attrsD: return
        self.links.append(urllib.parse.urljoin(self.baseuri, attrsD['href']))

def makeFullURI(uri):
    if (not uri.startswith('http://')) and (not uri.startswith('https://')):
        uri = 'http://%s' % uri
    return uri

def getLinks(data, baseuri):
    p = LinkParser(baseuri)
    p.feed(data)
    return p.links

def getALinks(data, baseuri):
    p = ALinkParser(baseuri)
    p.feed(data)
    return p.links

def getLocalLinks(links, baseuri):
    baseuri = baseuri.lower()
    urilen = len(baseuri)
    return [l for l in links if l.lower().startswith(baseuri)]

def isFeedLink(link):
    return link[-4:].lower() in ('.rss', '.rdf', '.xml', '.atom')

def isXMLRelatedLink(link):
    link = link.lower()
    return link.count('rss') + link.count('rdf') + link.count('xml') + link.count('atom')

def couldBeFeedData(data):
    data = data.lower()
    if '<html' in data: return 0
    if '<rss' in data or '<rdf' in data or '<feed' in data:
	    return 1

def isFeed(uri):
    _debuglog('verifying that %s is a feed' % uri)
    protocol = urllib.parse.urlparse(uri)
    if protocol[0] not in ('http', 'https'): return 0
    data = urllib.request.urlopen(uri).read()
    data = str(data, encoding='utf8')
    return couldBeFeedData(data)

def sortFeeds(feed1Info, feed2Info):
    return cmp(feed2Info['headlines_rank'], feed1Info['headlines_rank'])

def getFeedsFromSyndic8(uri):
    feeds = []
    try:
        server = xmlrpc.client.Server('http://www.syndic8.com/xmlrpc.php')
        feedids = server.syndic8.FindFeeds(uri)
        infolist = server.syndic8.GetFeedInfo(feedids, ['headlines_rank','status','dataurl'])
        infolist.sort(sortFeeds)
        feeds = [f['dataurl'] for f in infolist if f['status']=='Syndicated']
        _debuglog('found %s feeds through Syndic8' % len(feeds))
    except:
        pass
    return feeds
    
def getFeeds(uri, querySyndic8=0):
    fulluri = makeFullURI(uri)
    data = urllib.request.urlopen(fulluri).read()
    data = str(data, encoding='utf8')
    # is this already a feed?
    if couldBeFeedData(data):
        return [fulluri]
    # nope, it's a page, try LINK tags first
    _debuglog('looking for LINK tags')
    feeds = getLinks(data, fulluri)
    _debuglog('found %s feeds through LINK tags' % len(feeds))
    feeds = list(filter(isFeed, feeds))
    if not feeds:
        # no LINK tags, look for regular <A> links that point to feeds
        _debuglog('no LINK tags, looking at A tags')
        links = getALinks(data, fulluri)
        locallinks = getLocalLinks(links, fulluri)
        # look for obvious feed links on the same server
        feeds = list(filter(isFeed, list(filter(isFeedLink, locallinks))))
        if not feeds:
            # look harder for feed links on the same server
            feeds = list(filter(isFeed, list(filter(isXMLRelatedLink, locallinks))))
        if not feeds:
            # look for obvious feed links on another server
            feeds = list(filter(isFeed, list(filter(isFeedLink, links))))
        if not feeds:
            # look harder for feed links on another server
            feeds = list(filter(isFeed, list(filter(isXMLRelatedLink, links))))
    if not feeds and querySyndic8:
        # still no luck, search Syndic8 for feeds (requires xmlrpclib)
        _debuglog('still no luck, searching Syndic8')
        feeds = getFeedsFromSyndic8(uri)
    return feeds

##### test harness ######

def test():
    uri = 'http://diveintomark.org/tests/client/autodiscovery/html4-001.html'
    failed = []
    count = 0
    while 1:
        data = urllib.request.urlopen(uri).read()
        data = str(data, encoding='utf8')
        if data.find('Atom autodiscovery test') == -1: break
        sys.stdout.write('.')
        count += 1
        links = getLinks(data, uri)
        if not links:
            print('\n*** FAILED ***', uri, 'could not find link')
            failed.append(uri)
        elif len(links) > 1:
            print('\n*** FAILED ***', uri, 'found too many links')
            failed.append(uri)
        else:
            atomdata = urllib.request.urlopen(links[0]).read()
            atomdata = str(atomdata, encoding='utf8')
            if atomdata.find('<link rel="alternate"') == -1:
                print('\n*** FAILED ***', uri, 'retrieved something that is not a feed')
                failed.append(uri)
            else:
                backlink = atomdata.split('href="').pop().split('"')[0]
                if backlink != uri:
                    print('\n*** FAILED ***', uri, 'retrieved wrong feed')
                    failed.append(uri)
        if data.find('<link rel="next" href="') == -1: break
        uri = urllib.parse.urljoin(uri, data.split('<link rel="next" href="').pop().split('"')[0])
    print()
    print(count, 'tests executed,', len(failed), 'failed')
        
if __name__ == '__main__':
    if sys.argv[1:]:
        uri = sys.argv[1]
    else:
        uri = 'http://diveintomark.org/'
    if uri == 'test':
        test()
    else:
        print("\n".join(getFeeds(uri)))
