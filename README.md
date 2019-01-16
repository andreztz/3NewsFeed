## NewsFeed

NewsFeed is an RSS/RDF/Atom reader and aggregator written in Python
which uses Mark Pilgrim's Universal Feed Parser.

NewsFeed only depends on Tk, no other libraries are required.

For more detailed instructions, see the NewsFeed [home page](http://mdoege.github.io/3NewsFeed/) and [manual](http://mdoege.github.io/3NewsFeed/README.html).

![screenshot](https://github.com/mdoege/3NewsFeed/raw/master/newsfeed.png "NewsFeed screenshot")

### Quick Start Guide

Installation:

`python setup.py install`

If you just want to try NewsFeed out, no installation is necessary, simply run `newsfeed` or `Start_NewsFeed.py`.

### Keyboard shortcuts

Space, m, the arrow keys, and Return are the most important keys for everyday usage.

| Key | Function
| --- | ---
| Space | Jump to next unread item
| Return | Open item in browser
| Page up/down | Page up or down in current item
| Home/End | First/last page of item
| Up/Down | Previous/next item in feed
| Left/Right | Previous/next feed
| &lt; , &gt; , [ , ] |  Jump to last/next item in history
| c | Toggle night mode
| C (shift-c) | Catch up, i.e. mark all items in all feeds as read
| Backspace / d | Delete item
| e | Edit feed info
| h | Open feed home page
| i | Iconify app
| m | Mark all items in current feed as read
| n | Mark/unmark item as important. It will show up in the Important Items feed.
| N (shift-n) | Go to the Important Items search feed
| o | Toggle offline mode (suppress updates)
| q | Quit NewsFeed
| r | Refresh current feed
| R (shift-r) | Refresh all feeds
| s | Create new search feed
| v | Go to Recently Visited search feed
| w | Toggle widescreen mode
| x | Export current item
| Z (Shift-z) / z | Resize font used for the user interface and lists
| + / - | Resize font for item text
