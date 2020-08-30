#!/usr/bin/env python
# coding: utf-8

# In[102]:


import re
import pickle
import Stemmer
import numpy as np
from collections import defaultdict, OrderedDict
import sys


# In[103]:


re.split(':','b:Sachin c:world cup')


# In[104]:


STOP_DICT = {}
# INPUT_FILE = '../enwiki-20200801-pages-articles-multistream1.xml-p1p30303'
INDEX_DIR = 'index/'
QUERY = 'b:Sachin c:world cup'
if INDEX_DIR[-1]!='/':
    INDEX_DIR+='/'
STOP_DICT = {}
STOP_FILE = ''
if INDEX_DIR.split('/')[0] == '2018114017':
    STOP_FILE = '2018114017/stopwords.pickle'
else:
    STOP_FILE = 'stopwords.pickle'
with open(STOP_FILE, 'rb') as handle:
    STOP_DICT = pickle.load(handle)
handle.close()
stemmer = Stemmer.Stemmer('english')
f = open(INDEX_DIR+"index.txt", "r")
index_string = f.read()
f.close()
temp = index_string.split('\n')
index = defaultdict(list)
for i in temp:
    splits = i.split(':')
    index[splits[0]] = splits[1].split(' ')


# In[105]:


def preprocess(text):
    text = text.lower()
    tokens = re.sub(r'[^A-Za-z0-9]+', r' ', text).split()
    stemmed_stop_free = []
    for token in tokens:
        if token not in STOP_DICT:
            stemmed_stop_free.append(stemmer.stemWord(token))
    return stemmed_stop_free


# In[106]:


def parse_query(query):
    query_list = query.split(':')
    if len(query_list) == 1:
        return preprocess(query_list[0]) , 0
    else:
        query_dict = {}
        # query_dict[query_list[0]] = ''
        for i in range(1, len(query_list)-1):
            query_dict[query_list[i-1][-1]] = preprocess(query_list[i][:-2])
        query_dict[query_list[-2][-1]] = preprocess(query_list[-1])
        return query_dict, 1


# In[107]:


def run_whole_query(query):
    docs_intersect = []
    for i in range(len(query)):
        doc_list = []
        docs_postlist = {}
        post = []
        for j in index[query[i]]:
            splits = re.split('d|b|i|l|r|t|c', j)
            doc_list.append(splits[1])
            post.append(j)
        docs_postlist[query[i]]=post
        if i == 0:
            docs_intersect = doc_list
        else:
            docs_intersect = np.intersect1d(docs_intersect, doc_list)
    return docs_intersect


# In[108]:


def run_parsed_query(query_dict):
    flag = 0
    docs_intersect = []
    docs_postlist = {}
    for category in query_dict.keys():
        for i in range(len(query_dict[category])):
            doc_list = []
            post = []
            for j in index[query_dict[category][i]]:
                if category == 't':
                    splits = re.split('t', j)
                if category == 'b':
                    splits = re.split('b', j)
                if category == 'i':
                    splits = re.split('i', j)
                if category == 'c':
                    splits = re.split('c', j)
                if category == 'l':
                    splits = re.split('l', j)
                if category == 'r':
                    splits = re.split('r', j)
                if len(splits) > 1:
                    post.append(j)
                    splits2 = re.split('d|b|i|l|r|t|c', j)
                    doc_list.append(splits2[1])
                    docs_postlist[category+':'+query_dict[category][i]]=j
            docs_postlist[category+':'+query_dict[category][i]]=post
            if flag == 0:
                docs_intersect = doc_list
                flag = 1
            else:
                docs_intersect = np.intersect1d(docs_intersect, doc_list)
    return docs_intersect, docs_postlist


# In[109]:


def print_postlist(postlist):
    for i in postlist.keys():
        print("Postlist for",i+":")
        for j in postlist[i]:
            print(j,end=' ')
        print()
        print()


# In[112]:


parsed, querytype = parse_query(QUERY)
docs_intersect = []
docs_postlist = {}
if querytype == 0:
    docs_intersect, docs_postlist = run_whole_query(parsed)
else:
    docs_intersect, docs_postlist = run_parsed_query(parsed)
print_postlist(docs_postlist)


# In[111]:


querytype


# In[112]:




