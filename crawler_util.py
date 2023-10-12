"""
Web-Crawler utility functions. 

This module provides the HTMLGrabber utility class for loading and
parsing HTML documents.
                
Author: Nathan Sprague
Date: 12/31/2012

Updated to Python 3 by Mike Lam, August 2014
"""

# DO NOT MAKE ANY CHANGES TO THIS FILE!!!

import html.parser
import string
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser


class HTMLGrabber(html.parser.HTMLParser):
    """
    This class handles downloading and processing an HTML document.
    """

    def __init__(self, url, verbose=False):
        """Construct an HTMLGrabber object.

        This constructor downloads the HTML file at the indicated
        address and parses it in order to extract the page title, the
        page text and all outgoing links.

        Notes:
          - robots.txt is respected.  If the server doesn't want the
            file crawled, this function won't crawl it.
          - If any sort of exception occurs during processing, this
            function will quietly give up and subsequent calls to get_text etc.
            will return empty defaults.

         Parameters:
           url -     A string containing a valid absolute url.  Eg:
                     "http://www.jmu.edu" or
                     "file:///home/spragunr/somefile.html"
           verbose - If True, an error message will be printed if an
                     exception is encountered.  If False, exceptions
                     are quietly ignored.  Defaults to False.
        """
        html.parser.HTMLParser.__init__(self)
        self._url = url
        self._title = ""
        self._links = set()
        self._words = []
        self._in_bad_tag = False
        self._in_title = False

        try:
            if _check_url(url):
                fileHandle = urllib.request.urlopen(url, timeout=1)
                self.feed(str(fileHandle.read()))

        except Exception as ex:
            if verbose:
                print(("Exception raised while processing " + url + "\n  " + str(ex)))

    def get_title(self):
        """
        Return the HTML page title.  This may return an empty string
        if there were errors during parsing, or if the page has no
        title.
        """
        return self._title

    def get_text(self):
        """
        Return all of the document text as a single lower-case string.
        All Punctuation will be removed.  This may return an empty
        string if there were errors during parsing.
        """
        all_text = " ".join(self._words)
        no_punct = all_text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

        return no_punct.lower()

    def get_links(self):
        """Return all outgoing links from the HTML document.

        Notes:
        - Only one copy of each link will be returned.
        - All links are returned.  Returned links may or may not refer to HTML
          documents.

        Returns:
          An unordered list of strings, where each string is a URL.
        """
        return list(self._links)

    def get_url(self):
        """Returns a string containing the URL of this page."""
        return self._url

    # IGNORE THE METHODS BELOW.  These override methods provided by
    # HTMLParser.HTMLParser and will be called automatically during
    # parsing.  They should not be called directly.

    def handle_starttag(self, tag, attrs):
        """Overrides HTMLParser.HTMLParser.handle_starttag.

        This method should not be called directly!.  It will be called
        automatically when a start tag is reached during parsing."""

        if tag in ["style", "script"]:
            self._in_bad_tag = True
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    # Change relative URLs into absolute URLs
                    url = urllib.parse.urljoin(self._url, attr[1])

                    # Chop off anchors...
                    if url.find("#") != -1:
                        url = url[: url.find("#")]

                    self._links.add(url)

    def handle_endtag(self, tag):
        """Overrides HTMLParser.HTMLParser.handle_endtag.

        This method should not be called directly!.  It will be called
        automatically when an end tag is reached during parsing."""

        if tag in ["style", "script"]:
            self._in_bad_tag = False
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        """Overrides HTMLParser.HTMLParser.handle_data.

        This method should not be called directly!.  It will be called
        automatically when a data region is reached during parsing."""

        if not self._in_bad_tag and not self._in_title:
            # need to filter cruft that seems to have been introduced in the
            # port to Python 3:
            #
            #   - mangled whitespace characters (\\r, \\n, \\t)
            #   - unnecessary escapes (\\)
            #   - unexplicable "b'" strings
            #

            new_words = data.replace("\\r", "")
            new_words = new_words.replace("\\n", "")
            new_words = new_words.replace("\\t", "")
            new_words = new_words.replace("\\", "")
            self._words.extend(filter(lambda x: x != "b'", new_words.split()))
        if self._in_title:
            self._title += data


def _check_url(url):
    """
    This function checks the provided url to make sure that it links to
    an accessible HTML document.  It checks the appropriate robots.txt file
    as well as the mime type.
    """
    can_access = True

    # First make sure robots.txt allows access...
    o = urllib.parse.urlparse(url)
    if o.scheme != "" and o.netloc != "":
        rp = urllib.robotparser.RobotFileParser()
        robot_loc = o.scheme + "://" + o.netloc + "/robots.txt"
        rp.set_url(robot_loc)
        rp.read()
        can_access = rp.can_fetch("*", url)

    # Now make sure that the target is actually an HTML document...
    if can_access:
        f = urllib.request.urlopen(url, timeout=1)
        can_access = can_access and (f.info().get_content_type() == "text/html")

    return can_access


if __name__ == "__main__":
    # Just a little test code to see if everything is working correctly...
    url = "http://www.msit.ac.in/"
    info = HTMLGrabber(url, True)
    print(("Title: " + info.get_title() + "\n"))
    print(("Text: " + info.get_text() + "\n"))
    print(("Links: " + str(info.get_links()) + "\n"))
    print(("URL: " + info.get_url() + "\n"))
