## NewsFeed 3.4 Documentation

### Overview

NewsFeed is an RSS/RDF/Atom reader and aggregator for UNIX-like operating
systems, such as Linux, Mac OS X, FreeBSD, or Windows. It is written in Python
and uses Mark Pilgrim's Universal Feed Parser for downloading and parsing
feeds.

NewsFeed aims to be easy to setup and use and is something of a clone of
NetNewsWire. It only depends on Tk, no other libraries are required.

### Installation

If you just want to try NewsFeed out, no installation is necessary at all.
Simply untar the file, `cd` to the directory and run `./newsfeed`. As Python
can find packages in the current working directory as well as the global
locations, everything should work as expected.

If you want to install the program globally or under your home directory,
please choose one of the following two methods:

**Method A** (automatic install): Use the distutils approach. Untar the file
and then do `python setup.py install`. See the [distutils documentation][1]
for installation options like directory paths.

**Method B** (manual install):

  1. Copy `newsfeed.py`, `rssfinder.py`, `rssparser.py`, and `dlthreads.py`
into the Python module path, e.g. to
`/usr/local/lib/python2.7/site\-packages/` or to where your PYTHONPATH
environment variable points.

  2. By default, audio notifications are turned off. If you want them, set the
environment variable NEWSFEED_SOUND to the full path of a sound file. (Setting
it to "none" disables notification sounds.) *NOTE:* You need to have either
[PyAudio][8] or [Snack][2] installed to play notification sounds.

  3. Copy at least `newsfeed` and, if you need them, also `add_feed.py`,
`feed2opml.py`, `opml2feed.py`, `update_feeds.py`, and `dinos.py` to somewhere
in your $PATH.

If you want [auto\-subscription][3] to work you have to consult your web
browser documentation on how to add a handler for specific MIME types or
keywords, see below.

### The GUI

The NewsFeed main window features a familiar three\-pane layout similar to
many email programs, where in the left vertical pane the newsfeeds and active
searches are listed, with buttons right below to move the active feed up and
down in the list. Behind the entries the number of unread items in the feed is
shown in parentheses. Empty feeds or feeds that did not update correctly the
last time (e.g., because of a server timeout) are put in square brackets.
Right below the buttons is the progress bar, which is white normally, but
shows a green bar when an update is in progress.

Right next to the feed list is the items list for the selected feed, with
newest items at the top. Items that were already displayed are shown slightly
indented and in parentheses, whereas new, unread items are shown without
indentation. If available, the column right next to the one with the subject
lines shows the time stamps for the individual messages, or if not available,
for the feed.

Below the topic list is the main text area where the description of the
selected item is displayed. In the top right corner is again the date as
supplied by the feed if available, while in the lower right corner the
download date is shown in local time. The article headline is clickable and
will open the browser that is set in the BROWSER shell environment variable.
([Dillo][5] is a good choice for a browser in this context, as it starts up
very fast and displays most pages quite nicely.) Alternatively, pressing
**Return** opens the current item. The headline will turn violet if has been
visited in the browser. Finaly, the URI of the item is printed in a red font
below the text.

#### Top row buttons

  * 'Refresh Now' (Key **R**): Update all feeds. During updating the user
interface can become sluggish for a few seconds, so it is probably better to
wait for the update to complete. (Please not that as of v1.6 pressing **r**
now only updates the current channel.)

  * 'Edit Channel' (Key **e**): Edit the current channel's properties.
'Name' is what is shown in the channel list, if unsure, prepend a '?' to the
name, causing NewsFeed to look for the channel name in the newsfeed header.
'RSS' is the URI of the feed, if unknown, enter the URI of the site into 'Home'
and 'Press 'Auto\-Detect RSS Feed'. With luck, one or more channels will be
found for the site and merged into the channel list. 'Update every' marks the
update interval for that particular channel, while 'Expire after' is the time
for which the feed items are stored. Pressing 'Save Information' saves, while
closing the window cancels. Below the buttons the official channel description
by the newsfeed provider is shown.

  * 'Subscribe': Creates a new channel and opens its edit box. See
[auto\-discovery.][6]

  * 'Unsubscribe': Delete current channel (or search) from the list.

  * 'Search News' (Key **s**): Allows to search headlines and content for
words or phrases. Select 'Match Case' if capitalization is significant, select
'Match Whole Words' if your search terms should not be part of longer words.
Pressing **Return** or clicking 'Accept' adds the search to the feed list. It
gets updated automatically whenever one of the channels changes ("Live
Search").

  * 'Next Unread' (**Space**): Jump to the next unread item, either in this or
in other feeds. By repeatedly clicking this button, you can cycle through all
new items until none are left.

  * 'Mark All As Read' (Key **m**): Mark the entire channel contents as read.
There is also the catch up command (**C**, i.e. **Shift**\-**c**) which marks
all items in all channels as read.

  * 'Delete' (Key **d** or **Backspace**): Deletes the current item from the
feed and remembers _not_ to download it again (at least until the expiration
time set for the channel). This is useful to get rid of annoying items such as
"Customize this feed", ads, etc.

  * 'Delete All': Resets the current channel. If you refresh immediately, all
items currently available will be downloaded again. The delete commands can
also be used in a search, where they will affect the feeds in which the items
were found.

#### Other functionality

Note that window positions and sizes are saved when you move or resize the
windows. For the helper windows, this does not work if you close them with
their close buttons, you have to do 'Accept' or 'Save', respectively.

In the content pane, directly above the item title there is a toolbar (as of
v1.7) that contains buttons labeled "back" (Key **<** or Key **\[**) and
"forward" (Key **>** or Key **\]**) for navigating between read items in the
standard web browser fashion.

Pressing **q** quits the application. **Escape** can also be used to dismiss
the info and search windows.

Additionally, the **up** and **down** cursor keys go the previous/next item in
the feed, while the **left** and **right** cursor keys jump to the
previous/next feed. Finally, pressing **v** jumps to the history ("Recently
Visited") feed.

The "Important Items" feed contains items that were marked as important,
either by using the "Mark" button in the item pane toolbar or by using the
keyboard shortcut **n**. Items in this feed never expire and subject lines of
flagged items are prepended with "\!\!\!". You can use the keyboard shortcut
**N** (i.e. **Shift**\-**n**) to jump to this feed.

The font size in the item description pane can be adjusted with the "Smaller"
and "Larger" buttons from the item toolbar, or using the keyboard shortcuts
**\+** and **\-**.

The keyboard shortcut **i** iconifies the application (or puts it in the dock
on Mac OS X), **w** toggles widescreen mode, and **h** opens the homepage of
the feed (as given by the URL under "Home:" in the Channel Info window).

##### Item export

"Export" writes the currently selected item to a file and calls an application
with the filename as an argument. Lines 66 to 73 in `newsfeed.py` show how to
set this up using template substitution. You can use this feature e.g. to

  * create a new email with the item as the text body and its title as the
subject

  * print the item, for example using a2ps

  * export the item to a weblog editor

  * &hellip;or whatever else you can think of

##### Custom refresh intervals

Custom refresh intervals are implemented as a an item in the refresh interval
popup menu in the subscription info box, "Custom". The number of minutes this
interval corresponds to is set on line 83 of `newsfeed.py` in the variable
`custom_interval`. By default this is set to .333, i.e. about 20 seconds.

##### <a name="autodis">Auto-discovery of feed URLs</a>

If you want to try the auto\-discovery of feeds, enter an URL under "Home:" in
the Channel Info window and click "Auto\-Detect RSS Feed" (or just hit Return
if your are confident &#9786;). After a few seconds, one or more
auto\-detected feeds will appear in the feed list if the operation is
successful. The temporary feed names are prepended with question marks, which
tells NewsFeed to look for a feed name in the feed itself and use that.

Please also note that the Tkinter bindings to the Tk widget set tend to leak
memory, depending on the version of the bindings used. In other words, the
amount of memory occupied by NewsFeed may grow over time, even if it is mostly
idling. Therefore it may not be a good idea to leave NewsFeed running for a
prolonged period of time (days, weeks, or so) in a memory\-starved or
multi\-user environment.

### Console mode

There is a basic console interface (e.g. for running via SSH) which can be
activated with a command line option: `newsfeed \-\-nogui`. Select a feed from
the list by its number, then optionally select an item to open it in the
browser. Use "0" to go back or exit.

### Helper scripts

  * `add_feed.py`: Its command line argument has to be an RSS URL, which is
added to the list of feeds in Newsfeed either by signalling a running NewsFeed
instance or the next time the user starts NewsFeed.<br> So typing, e.g.
`add_feed.py http://hypertext.rmit.edu.au/~burgess/index.xml` at the command
line will add that feed and load it in NewsFeed if it is running.

  * `bsize.py`: Show how many bytes each feed uses in memory. (Only the
content of the feed is counted, not the additional overhead in Python for
managing objects.) If a feed uses a lot of memory and the program becomes
slow, consider lowering the caching time for that feed.

  * `dinos.py`: Locates "dinosaurs" in your subscription list, i.e. feeds for
which no new items have been downloaded in a long time. The feed might be dead
&mdash;then again, it might just have changed its URL. Remember, NewsFeed does
not change feed URLs on its own behind your back in response to HTTP status
codes, so you have to do it yourself if there is an address change.<br>This
script outputs a sorted list of feed names and their age in days, as measured
by the download time of the most recent item for all feeds for which this age
exceeds ten days. Obviously, you will find the most likely candidates for
"dinosaur" feeds at the top of the list. You can optionally specify a minimum
age on the command line, e.g. `dinos.py 15` for feeds that have received no
updates for at least 15 days.

  * `dumpfeed.py`: Dumps a feed's contents to the console, in the format
`_TITLE_ :: _DESCRIPTION_` with one item per line (but of course line breaks
in descriptions are also printed). For example, `dumpfeed.py Slashdot` print
the contents of the feed called 'Slashdot' to standard output. The match is
not case\-sensitive.

  * `export_flagged.py` and `export_unread.py`: Export flagged or unread
items, respectively, in HTML format to standard output. The result might even
validate as XHTML if the HTML markup in the indivual news items is conformant.
One usage scenario for `export_unread` is to export the unread items to read
them in a web browser and then later to start up NewsFeed and use **Shift\-C**
to mark those stories as read.

  * `feed2opml.py`: Exports you feed list to OPML format, prints to standard
output.

  * `opml2feed.py`: Reads a file with feed descriptions in OPML format and
adds them to the NewsFeed subscriptions list if they are not already in the
database (identified by their feed URI), so e.g. you would type `opml2feed
new_feeds.opml` to process the entries in `new_feeds.opml` and append them to
the list.<br>Note that NewsFeed should not be running while you do this, as
otherwise it will overwrite the changes. Also note that this script will have
to remove any active searches from your NewsFeed subscriptions list, as some
versions of Python may show unexpected behavior if the searches are kept. Of
course you can add them again after the import is complete.

  * `update_feeds.py`: Updates the NewsFeed cache from the command line. The
idea is that you invoke this script from a cron job that runs, say, every
hour. That way, feeds will be updated even when NewsFeed itself is not
running, so you don't miss any articles in between. Note that this script only
runs if no instance of NewsFeed is active to avoid conflicts over the
database. Also note that all feeds are updated regardless of their time of
last update. When an optional command line parameter is provided, `\-v`, this
script reports if an instance of NewsFeed is already running.

### Environment variables

  * `NEWSFEED_SOUND` &mdash; path to sound file to play when new items have
arrived

  * `BROWSER_NEW` &mdash; open stories in new window (as opposed to existing
window)? Can be either "yes" or "no".

  * `MEDIA_PLAYER` &mdash; program for handling enclosures

If these environment variables are not set, builtin defaults will be used.

### Upgrading and troubleshooting

Before you upgrade, copy your latest `~/.newsfeed` to a safe place, so you can
restore it should there be a problem.

If your `~/.newsfeed` configuration file is from an older version of NewsFeed,
the latest version might not import it, because `rssparser.py` was renamed to
`feedparser.py` at some point. Therefore, if NewsFeed overwrites the old
`.newsfeed` file with its default configuration, try to quit, copy the old
`.newsfeed` in its place again, copy `feedparser.py` to `rssparser.py`, and
relaunch.

### Configuration file and item store

By default, the configuation as well as the cached data is stored in
`~/.newsfeed`, while in `~/.newsfeed.pid` the PID of the currently running
NewsFeed instance is stored. Finally, `~/.newsfeed.addfeed` contains new URIs
from the helper script and should be processed (and then deleted) by the main
program.

As the entire program state is stored in the platform\-independent
`~/.newsfeed` file, one can sync NewsFeed to a different machine or restore a
previous state by copying / moving /renaming `~/.newsfeed`.

#### <a name="recov">Automatic versioning of the configuration/cache file</a>

Earlier versions of NewsFeed (up to 1.5.2) used only one copy of the
configuration/cache file. In the unlikely event that the computer crashed
while NewsFeed was in the midst of saving its state, the file could become
corrupted.

As of NewsFeed 1.6, the configuration file is versioned, that is, older
versions with the extensions `.1`, `.2`, `.3`, etc. are kept in case something
goes wrong with the main file.

This versioning mechanism is fully automatic and also features automatic
recovery, meaning that if the main configuration file is unreadable for some
reason, NewsFeed looks for older revisions of the file and uses the most
recent version.

If required, the number of old revisions to keep (which defaults to three) can
be set on line 86 in `newsfeed.py`. Also note that, as opposed to the
numbering scheme in [VMS][7], lower extensions denote more recent versions.

#### <a name="exc">Extra configuration file</a>

As of v2.6, NewsFeed also looks for the file
`newsfeed_defaults.py`&mdash;first in the current working directory, then in
the directory where `newsfeed.py` resides, then in the usual module search
path&mdash;and tries to import it. This file may contain definitions of global
variables which override the assignments at the top of `newsfeed.py`.

So for instance, you could have a `newsfeed_defaults.py` that contains:

    custom_interval = 1
    browser_cmd = "konqueror %s &"
    config_file = "/Users/martin/Public/testfile"
    fontscaling = 1.2
    ask_before_deletion = False

It would cause NewsFeed to

  1. set the custom refresh interval to one second,

  2. use a different command for opening the web browser (ignoring the BROWSER
environment variable),

  3. use a different location for the cache and configuration files,

  4. use bigger fonts at startup,

  5. and to disable the warning when deleting a feed.

This feature is mainly meant to facilitate keeping NewsFeed together with
Python/Tk and a lightweight web browser on a removable medium such as a USB
flash drive. In this case, `newsfeed_defaults.py` should be in the same
directory as the other Python scripts and minimally contain new definitions
for browser\_cmd (to point to the browser on the USB drive) and config\_file
(for NewsFeed to store its setting and cache on the drive as well).

### <a name="asub">Auto-subscription</a>

In principle, getting auto\-subscription, i.e. the appearance of new feeds in
NewsFeed when you click on them in the browser, to work would consist in
defining add_feed.py as a handler for files with ".rss" extensions. Now, apart
from the fact that some feeds have an ".xml" entension, browsers decide on
which program to use by MIME type.

Ideally, HTTP servers would be configured to send the MIME type
"application/xml\+rss" for files with "rss" extensions. Unfortunately, most
are not, sending "text/xml" or even "text/plain" instead. This complicates
auto\-subscription unnecessarily, because Mozilla likes to handle the latter
types internally.

Alternative solutions have been discussed at length, for instance prepending a
"feed:" to the URI or replacing the "http://" with a "feed://".  The
`add_feed.py` script supports all these mechanisms, but since there exists no
standard way of auto\-subscription right now, expect problems, at least with
some servers.

### Performance issues

Given that Python is a byte\-compiled language and that functional constructs
are used heavily by the program, NewsFeed may become sluggish if the
individual feeds have a lot of items. In that event, reducing the time for
which items are cached may be a good idea for feeds with many new items per
day (see `bsize.py`).

NewsFeed is not multithreaded, so it is perhaps advisable to simply leave it
alone while it is updating (as indicated by the white/green status bar in the
lower left corner), at least on high\-latency internet connections.

Generally, having searches in the feed list slows the program down. Thus, for
maximum performace, delete searches when you do not need them anymore.

   [1]: http://www.python.org/doc/current/inst/

   [2]: http://www.speech.kth.se/snack/

   [3]: #asub

   [4]: http://diveintomark.org/

   [5]: http://www.dillo.org/

   [6]: #autodis

   [7]: http://www.openvms.org/

   [8]: http://people.csail.mit.edu/hubert/pyaudio/

