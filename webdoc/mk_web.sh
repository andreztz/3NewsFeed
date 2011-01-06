#!/bin/sh

# Create HTML page for web site from Markdown source

Markdown.pl ../README.markdown > README2.html
cat header.txt README2.html footer.txt > ../README.html
rm README2.html
