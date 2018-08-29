#!/usr/bin/python


#   TODO:   some urls scraped are not of the correct format and crash the program eg https://twitter.com/itvfootball/status/1005921932473012224

"""
pip install bs4
pip install requests

"""
#import sqlite3
from bs4 import BeautifulSoup
import requests
import os


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
        self.page_limit = 0
        self.find_sub_pages = True
        self.prints_output = False
        self.prints_sub_page = False
        self.saves = True
        self.saves_sub_page = False

        #if not self.check_valid_input_arguments(self.page_limit, self.find_sub_pages, self.prints_output, self.saves):
        #    return
         

        if not args:
            self.get_main_page_info()
        else:
            for suffix in args:
                print ('Main Page: {}'.format(suffix))
                self.link_list.append(suffix)
                link = '{0}/news/{1}'.format(self.LINK_PREFIX, suffix)
                self.get_page_info_using_list(link, find_extra_pages = self.find_sub_pages, limit = self.page_limit, prints = self.prints_output, saves = self.saves)


    #def check_valid_input_arguments(self, page_lim_args, sub_pages_args, prints_args):
        #if self.page_limit < 0 :
        #    print ('Invalid INPUT ARGUMENTS!')
        #    return False
        #else:
        #    return True


    def get_main_page_info(self):
        
        r = requests.get('{}/news/'.format(self.LINK_PREFIX))
        
        if self.get_page_error(r.status_code):
            print("Error in trying to reach page: {}\n".format(r.url))
            return

        print("Searching  '{}'  for top articles".format(r.url))

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            most_read = soup.find("div", class_="nw-c-most-read gs-t-news gs-u-box-size no-touch b-pw-1280")
            header = "\n\t{0}\n".format(most_read.h2.text).expandtabs(32)
            stories = most_read.find_all("div", class_="gs-o-media__body")
            i = 1
        except:
            print("FAILED: \n\tUnable to scrape main page: '{}'\n".format(r.url).expandtabs(8))
            return

        print('{}\nAll top stories:'.format(header))

        for story in stories:
            self.all_stories[story.a.text] = story.a['href'] 
            link = '{}{}'.format(self.LINK_PREFIX, story.a['href'])
            print("\t{}.\t{}\n-> '{}'".format(i, story.a.text, link).expandtabs(8))
            self.get_page_info_using_list(link, prints = self.prints_output, find_extra_pages = self.find_sub_pages, limit = self.page_limit, saves = self.saves)
            i += 1


    def get_page_info_using_list(self, link, find_extra_pages = False, limit = 4, prints = False, saves = False):

        r = requests.get(link)

        if self.get_page_error(r.status_code):
            print("Error in trying to reach page: {}\n".format(r.url))
            return

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            article = soup.find('div', class_="story-body")
            tags = soup.find_all('div', class_="tags-container")
            header = '\n\t{0}\n'.format(article.h1.text).expandtabs(32)
            story = article.find('div', class_="story-body__inner")
            texts = story.find_all(['p', 'h2', 'img', 'figcaption'])

            all_text = ''

            for text in texts:
                if text.name == 'p':
                    if text.strong:
                        all_text += ''.join('\t{}\n'.format(text.strong.text.strip()).expandtabs(12))
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

            if saves:
                try:
                    file_name = '{0}.txt'.format(link[22:].strip().capitalize().replace("-", "_").replace("/", "-"))
                    print("Checking to se if ' {} ' already exists!".format(file_name))
                    path_to_file = 'news\{}'.format(file_name)
                    if os.path.exists(path_to_file):
                        print("The file exists!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    else:
                        print("The file does not exist ****************")                 
                        #   TODO: If link is a news link save to news folder
                        #         if sports  link save to sports foldar
                        with open(path_to_file, "w+") as file_to_save:
                            file_to_save.write('\n{0}{1}\n'.format(header, all_text))
                        print('\n\tSAVED!!!!!!!\n'.expandtabs(24))
                except:
                    print('\n\tUnable To Save File!\n'.expandtabs(24))
                #saves to file
        except:
            print("FAILED: \n\tUnable to scrape page: '{}'\n".format(r.url).expandtabs(8))
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
                print ("ERROR: \n\t{}\n".format(exp).expandtabs(8))
                return

            page_link = '{0}{1}'.format(self.LINK_PREFIX, main_tag)
            print ('\nLink to Sub-Page: {}'.format(page_link))
            source = requests.get(page_link)
            if self.get_page_error(source.status_code):
                print("Error in trying to reach related topics page: {}\n".format(r.url))
                return
            soup = BeautifulSoup(source.text, 'html.parser')
            links = soup.find_all('a', class_="lx-stream-asset__cta gel-long-primer-bold")
            for link in links:
                link = link['href'].split('?')[0]
                if link[:6] == '/news/' or link[:7] == '/sport/':
                    if i >= limit:
                        print('Max Number of sub_pages searched!')
                        break
                    if link not in self.link_list:
                        print('Page sublink: {}'.format(link))
                        self.link_list.append(link)

                        #   If its a sports page it wont scrape.
                        #   TODO: Create a Sports page scraper

                        subpage_link = '{0}{1}'.format(self.LINK_PREFIX,link)
                        i += 1
                        if link[:7] == '/sport/':
                            print("\tSPORT PAGE -\n\t\tUnable to scrape sports page yet: '{}'".format(subpage_link).expandtabs(4))
                            break
                        self.get_page_info_using_list(subpage_link, prints = self.prints_sub_page, saves = self.saves_sub_page)

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
    #WebScraper('world-asia-44158566')
    #print(WebScraper._WebScraper__private_variable)

    #   You can access private attributes as object._className__attrName
    #   print(web_scraper._WebScraper__private_variable)

if __name__ == '__main__':
    print ("WebScraper.__module__:\t{}".format(WebScraper.__module__))
    print ("WebScraper.__name__:\t{}".format(WebScraper.__name__))
    print ("WebScraper.__doc__:\t{}\n".format(WebScraper.__doc__))
    main()
    