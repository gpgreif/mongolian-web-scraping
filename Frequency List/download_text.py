import mechanize
import http.cookiejar
from bs4 import BeautifulSoup
import re

import pandas as pd
import time


#### USER ADJUSTMENTS ####

# Number of pages to read
n_pages = 2000

# How often to save
save_step = 20

# Whether to reset data
reset = False


if reset:
    method = 'w'
else:
    method = 'a'


#### FUNCTIONS ####

def load_new_urls(old_article_urls, count, n_pages=200):
    """Loads new urls to read, ignoring articles already accessed"""
    
    start_time = time.time()
    
    # List to save urls
    new_article_urls = set()

    for page in range(count, count + n_pages): #46790

        # URL to load
        url = 'https://news.mn/archive/page/' + str(page) + '/'

        # Loaded html
        html = br.open(url).read()

        # Read html with Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')

        # Find and print title to check we have loaded correctly
        print('Page ' + str(page) + ': ' + str(time.time() - start_time))

        # Find article urls
        for element in soup.find_all('article'):
            new_article_urls.add(element.a['href'])

    # Check we aren't rereading any articles
    new_article_urls = new_article_urls - old_article_urls

    print(time.time() - start_time)
    
    return new_article_urls

def download_text(br, new_article_urls):

    start_time = time.time()

    # Variables for new text, words, and phrases
    new_text = ""
    new_words = pd.Series(dtype='object')
    #new_two_word_phrases = pd.Series(dtype='object')
    #new_three_word_phrases = pd.Series(dtype='object')

    # Mongolian alphabet
    tolgoi = '[^АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоӨөПпРрСсТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя ]'

    for url, count in zip(new_article_urls, range(len(new_article_urls))):

        # Loaded html
        html = br.open(url).read()

        # Read html with Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')

        # Find and print title to check we have loaded correctly
        print('Article ' + str(count) + ': ' + soup.find('title').string)

        # Extract text from the article
        text = soup.find('div', class_='has-content-area').get_text()
        new_text += " " + text

        # Add words to word list
        article_word_list = pd.Series(re.sub(tolgoi, ' ', text).lower().split())
        new_words = new_words.append(article_word_list, ignore_index=True)
        
        """
        # Add phrases to phrase list
        two_word_phrases = (new_words.shift() + ' ' + new_words).dropna()
        three_word_phrases = (new_words.shift(2) + ' ' + new_words.shift() + ' ' + new_words).dropna()
        new_two_word_phrases = new_two_word_phrases.append(two_word_phrases, ignore_index=True)
        new_three_word_phrases = new_three_word_phrases.append(three_word_phrases, ignore_index=True)
        """
        
    time.time() - start_time

    return new_text, new_words #, new_two_word_phrases, new_three_word_phrases



for step in range(0, n_pages, save_step):


    #### SETTING UP URLS ####

    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = http.cookiejar.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.addheaders = [('User-agent', 'Chrome')]

    # Load old article urls to compare against
    old_article_urls = pd.read_csv('article_urls.csv', names=['url'])
    old_article_urls = set(old_article_urls['url'])

    # Load previous page count
    count = int(pd.read_csv('count.txt').columns[0])
    
    print("Loading URLs")
    
    # Load new urls
    new_article_urls = load_new_urls(old_article_urls, count, n_pages=save_step)




    #### DOWNLOADING TEXT AND WORDS ####
    
    print("Downloading text")
    
    # Download text, words, and phrases
    #new_text, new_words, new_two_word_phrases, new_three_word_phrases = download_text(br, new_article_urls)
    new_text, new_words = download_text(br, new_article_urls)

    # Append text to text file
    with open('text.txt', method) as f:
        f.write(new_text)

    # Append word and phrase lists to respective csv's
    new_words.to_csv('word_list.csv', mode=method, header=False, index=False)
    #new_two_word_phrases.to_csv('two_word_phrase_list.csv', mode=method, header=False, index=False)
    #new_three_word_phrases.to_csv('three_word_phrase_list.csv', mode=method, header=False, index=False)



    #### RECORDING ARTICLE URLS AND COUNT ####
    
    print("Recording article urls")
    
    # Record new urls in url file
    pd.Series(list(new_article_urls), dtype='object').to_csv('article_urls.csv', mode=method, header=False, index=False)

    # Update count
    with open('count.txt', 'w') as f:
        if reset:
            f.write('1')
        else:
            f.write(str(count + save_step))