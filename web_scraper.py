#!/usr/bin/python

"""
pip install bs4
pip install requests

"""
#import sqlite3
from bs4 import BeautifulSoup
import requests


class WebScraper:
    #   Calling WebScraper.__doc__ will return the string below
    'A Web Scraper Class that is used to scrape articles form the BBC News website.'
    #   Class variable, changed for all classes when changed
    LINK_PREFIX = 'https://www.bbc.co.uk'
    #   Private Variable starts with a double underscore: __private_var
    __private_variable = 1

    #   *args can be used when passing in a list / tuple of values as the functions parameters
    #   **kwargs can be used to pass through a dictionary of values as the functions parameters
    def __init__(self, *args): #(*args, **kwargs)
        
        #   Sets the instance variable of id equal to the private class variable of __private_variable
        self.id = WebScraper.__private_variable
        #   Increments the private class variable __private_variable by one so for every new instance the class variable is different
        WebScraper.__private_variable += 1
        #   Instance variable, changed for the difference instances of the class
        self.link_list = []
        self.all_stories = {}

        #   Input Arguments
        page_limit = 5
        find_sub_pages = True
        prints_output = False

        if not args:
            self.get_main_page_info()
            #   TODO: Go to the bbc homepage and get latest storied 
        else:
            for suffix in args:
                print ('Main Page: {}'.format(suffix))
                self.link_list.append(suffix)
                link = '{0}/news/{1}'.format(self.LINK_PREFIX, suffix)
                self.get_page_info_using_list(link, find_extra_pages = find_sub_pages, limit = page_limit, prints = prints_output)


    def get_main_page_info(self):
        
        r = requests.get('{}/news/'.format(self.LINK_PREFIX))
        
        if self.get_page_error(r.status_code):
            print("Error in trying to reach page: {}\n".format(r.url))
            return

        print("Searching  '{}'  for top articles".format(r.url))

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            most_read = soup.find("div", class_="nw-c-most-read gs-t-news gs-u-box-size no-touch b-pw-1280")
            header = "\n\t{0}\n".format(most_read.h2.text).expandtabs(30)
            stories = most_read.find_all("div", class_="gs-o-media__body")
            i = 1
        except:
            print("FAILED: \n\tUnable to scrape main page: '{}'\n".format(r.url).expandtabs(6))
            return

        print('{}\nAll top stories:'.format(header))

        for story in stories:
            self.all_stories[story.a.text] = story.a['href'] 
            link = '{}{}'.format(self.LINK_PREFIX, story.a['href'])
            print("\t{}.\t{}\n-> '{}'".format(i, story.a.text, link).expandtabs(6))
            self.get_page_info_using_list(link, prints = False, find_extra_pages = True)
            i += 1


    def get_page_info_using_list(self, link, find_extra_pages = False, limit = 4, prints = False):

        r = requests.get(link)

        if self.get_page_error(r.status_code):
            print("Error in trying to reach page: {}\n".format(r.url))
            return

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            article = soup.find('div', class_="story-body")
            tags = soup.find_all('div', class_="tags-container")
            header = '\n\t{0}\n'.format(article.h1.text).expandtabs(30)
            story = article.find('div', class_="story-body__inner")
            texts = story.find_all(['p', 'h2', 'img', 'figcaption'])

            all_text = ''

            for text in texts:
                if text.name == 'p':
                    if text.strong:
                        all_text += ''.join('\t{}\n'.format(text.strong.text.strip()).expandtabs(10))
                    elif text.a:
                        all_text += ''.join('\t{}  -- | {} | --\n'.format(text.a.text.strip(), text.a['href'].strip()).expandtabs(6))
                    else:
                        all_text += ''.join('{}\n'.format(text.text.strip()))
                elif text.name == 'h2':
                    all_text += ''.join('\n\t{0}\n'.format(text.text.strip()).expandtabs(20))
                elif text.name == 'img':
                    all_text += ''.join('*** {0} ***\n'.format(text['src'].strip()))
                elif text.name == 'figcaption':
                    captions = text.findAll('span', {'class':['off-screen', 'media-caption__text']})
                    for caption in captions:
                        all_text += ''.join('---[ {0} ]---\n'.format(caption.text.strip()))

            if prints:
                print('\n{0}{1}\n'.format(header, all_text))
        except:
            print("FAILED: \n\tUnable to scrape page: '{}'\n".format(r.url).expandtabs(6))
            return

        if find_extra_pages:
            i = 0
                        
            try:
                if len(tags) == 0:
                    raise ValueError('There are no Related Topics for this page')
                elif len(tags) == 1:
                    main_tag = tags[0].li.a['href']
                elif len(tags) == 2:
                    main_tag = tags[1].li.a['href']
            except ValueError as exp:
                print ("ERROR: \n\t{}\n".format(exp).expandtabs(6))
                return

            page_link = '{0}{1}'.format(self.LINK_PREFIX, main_tag)
            print ('Link to Sub-Page: ',page_link)
            source = requests.get(page_link)
            if self.get_page_error(source.status_code):
                print("Error in trying to reach related topics page: {}\n".format(r.url))
                return
            soup = BeautifulSoup(source.text, 'html.parser')
            links = soup.find_all('a', class_="lx-stream-asset__cta gel-long-primer-bold")
            for link in links:
                link = link['href'].split('?')[0]
                if i >= limit:
                    print('Max Number of sub_pages searched')
                    break
                if link not in self.link_list :
                    print('Page sublink: {}'.format(link))
                    self.link_list.append(link)
                    subpage_link = '{0}{1}'.format(self.LINK_PREFIX,link)
                    self.get_page_info_using_list(subpage_link, prints = prints)
                    i += 1
            print('Pages found: {}\n'.format(i))


    def get_page_error(self, status_code):
        if status_code != 200:
            print("Request code was : {}".format(status_code))
            if status_code >= 300 and status_code <= 308:               print ('Redirection not expected!')
            elif status_code >= 400 and status_code <= 499 and not 404: print ('Client error!')
            elif status_code == 404:                                    print ('404 Error!\t Page not found!')
            elif status_code >= 500 and status_code <= 511:             print ('Server error!')
            else:
                print('Information Code!')
                return False
            return True
        else:
            return False
 
def main():
    #link_suffixes = ['/news/world-asia-44158566', '/news/world-middle-east-44167900', '/news/world-middle-east-44210403']
    #web_scraper = WebScraper('world-asia-44158566', 'world-middle-east-44167900', 'world-middle-east-44210403')
    WebScraper()
    #print(WebScraper._WebScraper__private_variable)

    #   You can access private attributes as object._className__attrName
    #   print(web_scraper._WebScraper__private_variable)

if __name__ == '__main__':
    print ("WebScraper.__module__:\t{}".format(WebScraper.__module__))
    print ("WebScraper.__name__:\t{}".format(WebScraper.__name__))
    print ("WebScraper.__doc__:\t{}\n".format(WebScraper.__doc__))
    main()
    