#!/usr/bin/env python
# coding: utf-8

# Import the required libraries

# In[1]:


import xml.sax
import re
from collections import defaultdict, OrderedDict
import Stemmer
from os import path
import sys
import pickle
import time


# In the cell below, we have instantiated some global variables and initiated the stemmer

# In[2]:


#Need to change these below
INPUT_FILE = sys.argv[1]
OUTPUT = sys.argv[2]
INDEX_STAT = sys.argv[3]
TOTAL_TOKENS = 0
TOTAL_INV_TOKENS = 0
if OUTPUT[-1]!='/':
    OUTPUT+='/'
STOP_DICT = {}
STOP_FILE = ''
if OUTPUT.split('/')[0] == '2018114017':
    STOP_FILE = '2018114017/frequent.pickle'
else:
    STOP_FILE = 'frequent.pickle'
with open(STOP_FILE, 'rb') as handle:
    STOP_DICT = pickle.load(handle)
handle.close()
stemmer = Stemmer.Stemmer('english')
stem_dict = {}
title_dict = {}
indexMap = defaultdict(list)


# The preprocess function is to process the text. It tokenizes the data, removes unnecessary 
# non-ASCII characters and punctuations, stem the words using pystemmer and remove stop words

# In[3]:


def preprocess(text):
    tokens = re.sub(r'[^A-Za-z0-9]+', r' ', text).split()
    global TOTAL_TOKENS
    TOTAL_TOKENS += len(tokens)
    stemmed_stop_free = []
    for token in tokens:
        if token not in STOP_DICT:
            temp_stem = ''
            if token in stem_dict:
                temp_stem = stem_dict[token]
            else:
                stem_dict[token] = stemmer.stemWord(token)
                temp_stem = stem_dict[token]
            stemmed_stop_free.append(temp_stem)
            # stemmed_stop_free.append(stemmer.stemWord(token))
    return stemmed_stop_free


# The extract_under_ref function separates and preprocesses links, references and categories.
# The extract_infobox_and_refs separates and preprocesses infobox contents and references.

# In[4]:


def extract_under_ref(splits):
    if len(splits) == 1:
        return [], [], []
    else:
        data = splits[1].split('\n')
        links = []
        refs = []
        categories = []
        for line in data:
            if re.match(r'\*[\ ]*\[', line):
                links.append(line)
            if re.search(r'<ref', line):
                refs.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
            if re.match(r'\[\[category', line):
                categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))
        # return links, refs, categories
        return preprocess(' '.join(links)), preprocess(' '.join(refs)), preprocess(' '.join(categories))

def extract_infobox_and_refs(text):
    data = text.split('\n')
    flag = 0
    info = []
    refs2 = []
    for line in data:
        for i in re.findall("{{cite.*title=.*}}", line):
            refs2.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
        if re.match(r'\{\{infobox', line):
            flag = 1
            info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
        elif flag == 1:
            if line == '}}':
                flag = 0
                continue
            info.append(line)
    return preprocess(' '.join(info)), preprocess(' '.join(refs2))


# The split_page function splits a Wikipedia page into different parts like text, links, refs, body, categories

# In[5]:


def split_page( text):
    # text = text.encode("ascii", errors="ignore").decode()
    text = text.lower()
    splits = re.split(r'== ?references.?.? ?==|== ?notes and references ?==',text)
    # global pageCount
    # global titlefile
    # pageCount += 1
    # if pageCount%1000 == 0:
    #     print(pageCount)
    if (len(splits)==1):
        splits = re.split(r'== ?footnotes ?==', splits[0])
    data = {}
    data['links'], data['refs'], data['categories'] = extract_under_ref(splits)
    data['text'] = preprocess(re.sub(r'\{\{.*\}\}', r' ', splits[0]))
    data['infobox'], data['refs2'] = extract_infobox_and_refs(splits[0])
    data['refs'] = data['refs'] + data['refs2']
    return data


# The indexify function converts the document into inverted index

# In[6]:


def indexify(data):
    global indexMap
    totalFreq = defaultdict(lambda: 0)
    inverted = {}
    for i in ['title','text','infobox','categories','links','refs']:
        d = defaultdict(lambda: 0)
        for word in data[i]:
            d[word] += 1
            totalFreq[word] += 1
        inverted[i] = d
    for word in totalFreq.keys():
        string = 'd'+str(data['id'])
        for i in ['title','text','infobox','categories','links','refs']:
            temp = inverted[i][word]
            if temp:
                if i != 'text':
                    string += i[0] + str(temp)
                else:
                    string += 'b' + str(temp)
        indexMap[word].append(string)


# The xml_handler class is used to parse he xml file and call all the above functions

# In[7]:


class xml_handler( xml.sax.ContentHandler ):
    def re_init(self):
        self.title = ''
        self.text = ''
        # self.hashed = 0
        self.id = ''
        self.pages += 1
    def __init__(self, start_time):
        self.CurrentData = ''
        self.title = ''
        self.text = ''
        self.id = ''
        self.link_len = 0
        self.ref_len = 0
        self.categories_len = 0
        self.text_len = 0
        self.title_len = 0
        self.info_len = 0
        self.pages = 0
        self.start_time = start_time
        # self.hashed = 0

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag

    # Call when an elements ends
    def endElement(self, tag):
        if tag == 'page':
            # wiki_page = Page( self.title, self.text, self.id )
            # pages.append(wiki_page)
            data = split_page(self.text)
            data['title'] = preprocess(self.title)
            data['id'] = self.pages
            # if data['refs2'] == []:
            #     print(self.pages)
            # if data['id'] == 0:
            #     print(data)
            title_dict[self.pages] = self.title
            indexify(data)
            self.link_len += len(data['links'])
            self.info_len += len(data['links'])
            self.ref_len += len(data['refs'])
            self.categories_len += len(data['categories'])
            self.text_len += len(data['text'])
            self.title_len += len(data['title'])
            
            self.re_init()
            if self.pages %1000 == 0:
                print(self.link_len, self.ref_len, self.categories_len, self.text_len)
                print("Finished:", self.pages, "pages. Time elapsed:",time.time() - self.start_time )

    # Call when a character is read
    def characters(self, content):
        if self.CurrentData == 'title':
            self.title += content
        if self.CurrentData == 'text':
            self.text += content
        # if self.CurrentData == 'id' and not self.hashed:
        #     self.id = content
        #     self.hashed = 1


# The store_index function stores the index and index stats in files

# In[8]:


def store_index():
    index_map_file = []
    for key in sorted(indexMap.keys()):
        string = key + ':' + ' '.join(indexMap[key])
        index_map_file.append(string)
    with open(OUTPUT+'index.txt',"w+") as f:
        f.write('\n'.join(index_map_file))
    with open(INDEX_STAT,"w+") as f:
        f.write(str(TOTAL_TOKENS)+'\n')
        f.write(str(len(indexMap))+'\n')


# The wiki_parse function calls the xml_handler class and starts parsing the xml file. It also measures the time taken to parse the files.

# In[9]:


def wiki_parse(xml_file):
    print("Starting parser")
    parse_start_time = time.time()
    xml_parser = xml.sax.make_parser()
    xml_parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = xml_handler(parse_start_time)
    xml_parser.setContentHandler(handler)
    xml_parser.parse(xml_file)
    print("Parsing finished")
    parse_end_time = time.time()
    print("Total time taken: ",parse_end_time - parse_start_time)
    store_index()
    print("Dumping finished")
    print("Time taken: ",time.time() - parse_end_time)


# In[10]:


wiki_parse(INPUT_FILE)