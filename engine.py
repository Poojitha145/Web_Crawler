"""
Search Engine Class
Author: 
Date:
"""

import crawler_util


class SearchResult:
    """
    This is a simple container class for storing search results

    Public Attributes:
       url -   A string containing the URL of an HTML document.
       title - A string containing the title of the HTML page.
    """

    # DO NOT MODIFY THIS CLASS.

    def __init__(self, url, title):
        """Initialize the search result object."""
        self.url = url
        self.title = title

    def __eq__(self, rhs):
        """Override the == operator.
        Search results are considered equal if they have the same url.
        """
        return type(self) == type(rhs) and self.url == rhs.url

    def __hash__(self):
        """Return hash of search result."""
        return hash(self.url)


class SearchEngine:
    """
    The SearchEngine class is responsible for crawling some collection
    of HTML documents and creating an index that maps from words in
    those documents to SearchResult objects containing URLs and page
    titles.  This class also provides a method for searching the index
    once it is created.
    """

    def __init__(self):
        """
        Construct a SearchEngine.
        At the time of construction the index is empty.
        """
        # YOUR CODE HERE (Hint: Use a dictionary to store the search index and a set for keeping track of which URLs
        # have already been crawled
        self.ind = {}
        self.visited_urls = set()

    def crawl(self, url, max_depth):
        """
        Update the index by crawling a collection of HTML documents.

        The crawl begins at url and will visit all pages within max_depth links.
        For example, if max_depth = 0, only the document located at the
        indicated url is indexed. If max_depth = 2, the original document is
        indexed, along with all documents that it links to and all of the
        documents that THOSE documents link to.  This method tracks which URLs
        have already been visited so that no URL will be processed more than
        once.

        Arguments:
           url      -    A string containing a valid URL.  For example:
                        "http://www.jmu.edu" or
                        "file:///home/spragunr/somefile.html"
           max_depth -   The maximum crawl depth.  See explanation above.

         No return value.
        """
        # YOUR CODE HERE
        # print("before recursion")
        def crawl_recursion(c_url,c_depth):
            #if current depth is greater than max depth, just return
            if c_depth>max_depth:
                return

            #if curr_url is already present in crawled_urls set, then return
            if c_url in self.visited_urls:
                return

            #else add the curr_url to the set.
            self.visited_urls.add(c_url)
            print(self.visited_urls)
            #HTMLGrabber object to use get_text() and get_links() functions
            html_grabber=crawler_util.HTMLGrabber(c_url,False)

            #text present in the url
            web_text=html_grabber.get_text()
            # print("url_text",url_text)
            #links from that url
            web_links=html_grabber.get_links()
            # print("url_links",url_links)
            # url_title=html_grabber.get_title()
            word_list=web_text.split()
            for word in word_list:
                word=word.lower()
                # print("word",word)
                if word not in self.ind:
                    self.ind[word]=[]
                if c_url not in self.ind[word]:
                    self.ind[word].append(c_url)

            #reccursive do the operation for all the related links
            for link in web_links:
                crawl_recursion(link,c_depth+1)



        crawl_recursion(url,1)

    def search(self, word):
        """
        Return a list of SearchResult objects that match the given word.

        This function returns a (possibly empty) list of SearchResult
        objects.  Each object refers to a document that contains
        the indicated word.  The search is NOT case sensitive.

        This method will accept any string, but assumes that the string
        represents a single word.  Since the index only stores individual
        words, any strings with spaces or punctuation will necessarily
        have 0 hits.

        Arguments:
          word - A string to search for in the search engine index.

          Return: A list of SearchResult objects.  The order of the
                  objects in the list is not specified.
        """
        # YOUR CODE HERE.
        def get_title_from_url(url):
            html_grabber=crawler_util.HTMLGrabber(url)
            title=html_grabber.get_title()
            return title

        word=word.lower()
        if word in self.ind:
            url_list=self.ind[word]
            res=[]
            for i in range(len(url_list)):
                url=url_list[i]
                title=get_title_from_url(url)
                search_result_object=SearchResult(url,title)
                res.append(search_result_object)
            # res=[SearchResult(url,get_title_from_url(url)) for url in url_list]
            return res
        else:
            return []
        # pass


if __name__ == "__main__":
    # TESTING CODE HERE

    url = input("Enter URL to crawl:").strip()
    depth = int(input("Depth:"))

    search_engine = SearchEngine()
    search_engine.crawl(url, depth)

    print("\n")

    search_term = input("Enter search term:").strip()
    print("\n")

    if search_term.upper() != "EXIT":
        results = search_engine.search(search_term)
        print("Results:")
        for search_result in results:
            print(search_result.title)
            print(search_result.url)
            print("\n")
    else:
        print("Thank you for using text search engine")
