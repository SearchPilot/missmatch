Miss Match
============================

Miss Match is a HTML Parser designed to identify mismatched HTML tags.

It will report tags that haven't been opened correctly, e.g.:

`<div></p></div>` 

and tags that haven't been closed correctly: 

`<div><p></div>`

Installation
-------------

Installation via pip is not available (yet). For now just clone this repository, and install requests.


Usage 
------------

`python main.py http://www.example.com`


