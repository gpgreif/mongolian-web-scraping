import mechanize
import http.cookiejar
from bs4 import BeautifulSoup
import re

import pandas as pd
import time

#### USER INPUT ####

examples = False


#### CODE ####

start_time = time.time()

# Load text data
with open('text.txt', 'r') as f:
    text = f.read()
text = text.replace(u'\xa0', ' ')

# Load word list
word_list = pd.read_csv('word_list.csv', names=['Mongolian'])['Mongolian']

print('Loaded Word List:', time.time() - start_time)

# Compute frequencies and save
frequency_list = pd.DataFrame({'Count': word_list.value_counts()})
frequency_list.index.rename('Word', inplace=True)
frequency_list.to_excel('frequency_list.xlsx')

print('Saved Frequencies:', time.time() - start_time)

if examples:
    # Find example sentences
    for word in frequency_list.index:
        examples = re.findall(r"([^.]*?" + word + "[^.]*\.)", text)
        examples = list(filter (lambda example: (len (example) < 50) & (len (example) > 20), examples))[0:3]
        examples = "\n".join(examples)
        frequency_list.loc[word, 'Examples'] = examples
        print(word + ': ' + str(time.time() - start_time))
    
    # Save examples
    frequency_list.to_excel('frequency_list_with_examples.xlsx')

print('Total Time:', time.time() - start_time)