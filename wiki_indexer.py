#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xml.sax
import re
from collections import defaultdict, OrderedDict
import Stemmer
from os import path
import sys
import pickle
import time


# Need to change these below

# In[2]:


INPUT_FILE = sys.argv[1]
OUTPUT = sys.argv[2]
if OUTPUT[-1]!='/':
    OUTPUT+='/'
STOP_DICT = {}
STOP_FILE = ''
if OUTPUT.split('/')[0] == '2018114017':
    STOP_FILE = '2018114017/stopwords.pickle'
else:
    STOP_FILE = 'stopwords.pickle'
with open(STOP_FILE, 'rb') as handle:
    STOP_DICT = pickle.load(handle)
handle.close()
stemmer = Stemmer.Stemmer('english')
stem_dict = {}
title_dict = {}
indexMap = defaultdict(list)


# In[3]:


def preprocess(text):
    tokens = re.sub(r'[^A-Za-z0-9]+', r' ', text).split()
    stemmed_stop_free = []
    for token in tokens:
        if token not in STOP_DICT:
            if token in stem_dict:
                stemmed_stop_free.append(stem_dict[token])
            else:
                stem_dict[token] = stemmer.stemWord(token)
                stemmed_stop_free.append(stem_dict[token])
            # stemmed_stop_free.append(stemmer.stemWord(token))
    return stemmed_stop_free


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
        if re.match(r'\{\{infobox', line):
            flag = 1
            info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
        elif flag == 1:
            if line == '}}':
                flag = 0
                continue
            info.append(line)
        for i in re.findall("{{cite.*title=.*}}", line):
            refs2.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
    return preprocess(' '.join(info)), preprocess(' '.join(refs2))
# def getReferences(self, text):

#     data = text.split('\n')
#     refs = []
#     for line in data:
#         if re.search(r'<ref', line):
#             refs.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))

#     return self.process(' '.join(refs))


# def getCategories(self, text):
    
#     data = text.split('\n')
#     categories = []
#     for line in data:
#         if re.match(r'\[\[category', line):
#             categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))
    
#     return self.process(' '.join(categories))


# def getExternalLinks(self, text):
    
#     data = text.split('\n')
#     links = []
#     for line in data:
#         if re.match(r'\*[\ ]*\[', line):
#             links.append(line)
    
#     return self.process(' '.join(links))


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
    # data['infobox']

    # print(self.title)
    # titlefile = open('./index/titles','a')
    # string = str(self.id)+' '+self.title
    # string = string.strip().encode("ascii", errors="ignore").decode() + '\n'
    # titlefile.write(string)
    # titlefile.close()

    # self.infobox = self.getInfobox(data[0])
    # self.text = self.getBody(data[0])
    # self.title = self.getTitle(self.title)

    # print(self.title)
    # titlefile.write(str(self.id)+' '+self.title)

    # return self


# In[6]:


def indexify(data):
    # global pageCount
    # global fileCount
    global indexMap
    # global offset
    # global dictID
    # global filemap

    # ID = pageCount
    totalFreq = defaultdict(lambda: 0)

    d = defaultdict(lambda: 0)
    for word in data['title']:
        d[word] += 1
        totalFreq[word] += 1
    title = d
    
    d = defaultdict(lambda: 0)
    for word in data['text']:
        d[word] += 1
        totalFreq[word] += 1
    body = d

    d = defaultdict(lambda: 0)
    for word in data['infobox']:
        d[word] += 1
        totalFreq[word] += 1
    info = d

    d = defaultdict(lambda: 0)
    for word in data['categories']:
        d[word] += 1
        totalFreq[word] += 1
    categories = d
    
    d = defaultdict(lambda: 0)
    for word in data['links']:
        d[word] += 1
        totalFreq[word] += 1
    links = d
    
    d = defaultdict(lambda: 0)
    for word in data['refs']:
        d[word] += 1
        totalFreq[word] += 1
    references = d

    for word in totalFreq.keys():
        t = title[word]
        b = body[word]
        i = info[word]
        c = categories[word]
        l = links[word]
        r = references[word]
        string = 'd'+str(data['id'])
        if t:
            string += 't' + str(t)
        if b:
            string += 'b' + str(b)
        if i:
            string += 'i' + str(i)
        if c:
            string += 'c' + str(c)
        if l:
            string += 'l' + str(l)
        if r:
            string += 'r' + str(r)
    
        indexMap[word].append(string)
    
    # print(indexMap)

    # if pageCount%20000 == 0:
    

    #     indexMap = defaultdict(list)
    #     dictID = {}
    #     orderedMap = []
    #     fileCount += 1


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
            self.ref_len += len(data['refs'])
            self.categories_len += len(data['categories'])
            self.text_len += len(data['text'])
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


# In[8]:


def store_index():
    orderedMap = []
    for key in sorted(indexMap.keys()):
        string = key + ':'
        posting_list = indexMap[key]
        string += ' '.join(posting_list)
        orderedMap.append(string)
    with open(OUTPUT+'index.txt',"w+") as f:
        f.write('\n'.join(orderedMap))


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
    # pickle_out = open("index.pickle","wb")
    # pickle.dump(indexMap, pickle_out)
    # pickle_out.close()
    print("Dumping finished")
    print("Time taken: ",time.time() - parse_end_time)


# In[10]:


wiki_parse(INPUT_FILE)


# In[11]:


# count = 0
# t_list = []
# for i in indexMap['egypt']:
#     splits = re.split('c',i)
#     if(len(splits) > 1):
#         t_list.append(preprocess(title_dict[int(re.split('d|b|i',splits[0])[1])].lower()))
#         print(int(re.split('d|b|i',splits[0])[1]))
# print(count)


# In[12]:


# for i in range(len(title_dict)):
#     if preprocess(title_dict[i].lower()) == ['kellogg', 'briand', 'pact']:
#         print(i)


# In[13]:


# string = 'Ancient Egypt; Abydos, Egypt; Amasis II; Ammonius Saccas; Ababda people; Aswan; Abbas II of Egypt; Ambrose of Alexandria; Alexandria; Athanasius of Alexandria; Anthony the Great; Basel Convention; Battle of the Nile; Battle of Actium; Convention on Biological Diversity; CITES; Environmental Modification Convention; Cairo; Clement of Alexandria; Cyril of Alexandria; Coptic Orthodox Church of Alexandria; Duke Nukem 3D; Diophantus; Geography of Egypt; Demographics of Egypt; Politics of Egypt; Economy of Egypt; Telecommunications in Egypt; Transport in Egypt; Egyptian Armed Forces; Foreign relations of Egypt; Book of Exodus; First Battle of El Alamein; Go Down Moses; Great Pyramid of Giza; Great Rift Valley; Herodotus; History of Egypt; International Tropical Timber Agreement, 1983; International Tropical Timber Agreement, 1994; Imhotep; Kyoto Protocol; Kellogg–Briand Pact; Lighthouse of Alexandria; Library of Alexandria; Maimonides; Montreal Protocol; Mark Antony; Metre Convention; Muslim Brotherhood; Munich massacre; Nile; Treaty on the Non-Proliferation of Nuclear Weapons; Ozymandias; Origen; Pachomius the Great; Prospero Alpini; Pompey; Ptolemy; Ptolemaic dynasty; Palestine Liberation Organization; Red Sea; Rosetta Stone; Return to Castle Wolfenstein; Saladin; Sahara desert (ecoregion); Sinai Peninsula; Stargate (film); Saluki; Suez Canal; Six-Day War; Second Battle of El Alamein; Tax'
# gaurang = string.split(';')
# g_list = []
# for i in gaurang:
#     g_list.append(preprocess(i.lower()))


# In[14]:


# for element in g_list:
#     if element not in t_list:
#         print(element)


# In[15]:


# indexMap['egypt']


# In[16]:


# for i in ['2510', '12182', '13075', '19205']:
#     print(title_dict[int(i)], end='; ')


# In[17]:


# line = '{{cite news|last=Rendell|first=Ruth|authorlink=Ruth Rendell|title=A most serious and extraordinary problem |url=https://www.theguardian.com/books/2008/sep/13/arthurconandoyle.crime|newspaper=[[The Guardian]]|date= 12 September 2008|accessdate=8 December 2018}}'
# re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line)


# In[18]:




