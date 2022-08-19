import nltk
import re
import xml.etree.ElementTree as ET
import Stemmer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
from collections import OrderedDict
import sys
import os
import gc

from timeit import default_timer as timer
from datetime import timedelta

from yaml import events
import string 

path_to_dump = ""
path_to_index = ""
path_to_stats = ""

# Constants for the schema of inverted index
ID = 0
TITLE = 1
INFOBOX = 2
BODY = 3
CATEGORY = 4
LINKS = 5
REFERENCES = 6
PLAIN = 7


DA = 0

start = 0

initial_unique_tokens = set()
stopedwords = stopwords.words('english')
stemmed_word = {}
stemmer = Stemmer.Stemmer('english')
stemmer.maxCacheSize = 1000000

invidx = {}

def strip_tag_name(t):
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx+1:]
    return t

def get_info_box(text):
    global DA
    infop = re.compile("\{\{Infobox")
    # print(infop)
    m = infop.search(text)
    # if not m:
    #     infop = re.compile("\{\{Infobox")
    #     m = infop.search(text)
    if m:
        # print(m)
        # print(text[m.start():m.end()])
        infobox_start = m.end()
        i = m.start() + 1
        cnt = 1
        while(cnt > 0):
            if text[i] == '{':
                cnt = cnt + 1
            if text[i] == "}":
                cnt = cnt - 1
            i+=1
            if i >= len(text):
                DA += 1
                break
        infobox_end = i

        return text[infobox_start:infobox_end], text[:m.start()] + text[infobox_end:]
        # print(text[infobox_start:infobox_end])
    else:
        return "", text
        

def get_categories(text):
    infoc = re.compile("\[\[বিষয়শ্রেণীসমূহ:")
    m = infoc.search(text)
    if m:
        return text[m.start():], text[:m.start()]
    else:
        return "", text

def get_external_links(text):
    infoe = re.compile("== ?বহিঃসংযোগ ?==")
    m = infoe.search(text)
    if m:
        return text[m.end():], text[:m.start()]
    else:
        return "", text

def get_references(text):
    infor = re.compile("== ?(পাদটীকা|তথ্যসূত্র|তথ্য নির্দেশ) ?==")
    m = infor.search(text)

    text_r = ""
    text_left = text
    if m:
        text_r = text[m.end():]
        text_left = text[:m.start()]
    text_r += " "
    # print(text_left)
    # Now get reflist and update text_left and text_r

    # print("**************************")
    # print("**************************")
    # print("**************************")
   
    parts_to_remove = []

    stref = re.compile("<ref[^(/>)]*>")
    iterator = stref.finditer(text_left)
    # print(iterator)
    start_ref = []
    for match in iterator:
        # print(match.span())
        start_ref.append(match.span())
    
    enref = re.compile("</ref>")
    iterator = enref.finditer(text_left)
    # print(iterator)
    end_ref = []
    for match in iterator:
        # print(match.span())
        end_ref.append(match.span())

    singleref = re.compile("<ref [^(/>)]*/>")
    iterator = singleref.finditer(text_left)
    for match in iterator:
        parts_to_remove.append(match.span())
    # print(parts_to_remove)
    if len(start_ref) == len(end_ref):
        for i in range(len(start_ref)):
            parts_to_remove.append((start_ref[i][0], end_ref[i][1]))
    # print(parts_to_remove)
    parts_to_remove.sort()
    # print(parts_to_remove)
    # print(start_ref)
    # print(end_ref)
    # print(parts_to_remove)
    # m = infor.findall(text_left)
    # print(m)

    if len(parts_to_remove) > 0:
        new_text = ""
        lp = 0
        for tup in parts_to_remove:
            new_text += text_left[lp:tup[0]]
            lp = tup[1]
            text_r += " " + text_left[tup[0]:tup[1]]
        new_text += text_left[lp:]
        text_left = new_text

    return text_r, text_left

def parsePage(page):
    global DA
    # if page["id"] != 4:
    #     return
    # else:
    #     return
    parsedPage = {"id": page["id"], "title": page["title"]}
    text = page["text"]
    if text == None:
        text = ""
        # print(page)
    infobox, text = get_info_box(text)
    # print(text)
    # print("-----")
    # print("-----")
    # print(infobox)
    # Infobox parsed and removed from text
    parsedPage["infobox"] = infobox

    # Now getting categories
    categories, text = get_categories(text)
    
    # print(categories)
    # print("------")
    # print(text)
    # print("[][][][][][][][][][][][]\n\n\n")
    
    # Categories parsed and removed from text
    parsedPage["categories"] = categories

    # Now getting external links
    external_links, text = get_external_links(text)
    # print(external_links)
    # print("-----------")
    # print(text)
    # print("[][][][][][][][][][][][]\n\n\n")

    # External links parsed and removed from text
    parsedPage["external_links"] = external_links

    # Now getting references
    references, text = get_references(text)
    # print(references)
    # print("-----------")
    # print(text)
    # print("[][][][][][][][][][][][]\n\n\n")

    # References are parsed and removed from text
    parsedPage["references"] = references

    # Rest of the text as a whole is considered as the body
    parsedPage["body"] = text

    # print(parsedPage)

    return parsedPage
    # print(parsedPage)

    # print("---------------\n\n\n\n\n")


freq_count = {}


def tokenizePage(page):
    global freq_count
    keys = ["title", "infobox", "categories", "external_links", "references", "body"]
    for key in keys:
        tmp = "".join([char  if char.isascii() is False or char in string.digits else ' ' for char in page[key]]).strip().split()

        # for x in tmp:
        #     if x in freq_count:
        #         freq_count[x]+=1
        #     else:
        #         freq_count[x]=1

        page[key] = tmp
    return page
    # # print(page)
    # # print("--------------")
    # # print("--------------")
    # pattern = r'''(?x)          # set flag to allow verbose regexps
    #     (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
    #   | \w+(?:-\w+)*        # words with optional internal hyphens
    #   | \d+  # currency and percentages, e.g. $12.40, 82%
    # '''
    # page["title"] = nltk.regexp_tokenize(page["title"], pattern)
    # page["infobox"] = re.sub(r'http\S+', '', page["infobox"])
    # page["infobox"] = re.sub(r'\d+-[^ }]*', ' ', page["infobox"])
    # page["infobox"] = nltk.regexp_tokenize(page["infobox"], pattern)
    # page["categories"] = re.sub(r'\d+-[^ }]*', ' ', page["categories"])
    # page["categories"] = nltk.regexp_tokenize(page["categories"], pattern)
    # page["external_links"] = re.sub(r'http\S+', '', page["external_links"])
    # page["external_links"] = re.sub(r'\d+-[^ }]*', ' ', page["external_links"])
    # page["external_links"] = nltk.regexp_tokenize(page["external_links"], pattern)
    # page["references"] = re.sub(r'http\S+', '', page["references"])
    # page["references"] = re.sub(r'\d+-[^ }]*', ' ', page["references"])
    # page["references"] = nltk.regexp_tokenize(page["references"], pattern)
    # page["body"] = re.sub(r'(http\S+)|(www\.\S+)', '', page["body"])
    # page["body"] = re.sub(r'urlname=\w+', '', page["body"])
    # page["body"] = re.sub(r'\d+-[^ }]*', ' ', page["body"])
    # page["body"] = re.sub(r'\d{5,}', ' ', page["body"])
    # page["body"] = nltk.regexp_tokenize(page["body"], pattern)

    # # page["title"] = nltk.word_tokenize(page["title"])
    # # page["infobox"] = nltk.word_tokenize(page["infobox"])
    # # page["categories"] = nltk.word_tokenize(page["categories"])
    # # page["external_links"] = nltk.word_tokenize(page["external_links"])
    # # page["references"] = nltk.word_tokenize(page["references"])
    # # page["body"] = nltk.word_tokenize(page["body"])

    # # print(page)
    
    return page

def shortAndAscii(s):
    try:
        s.encode(encoding="utf-8").decode("ascii")
    except UnicodeDecodeError:
        return False
    else:
        return True

def check_and_remove_non_ascii(section):
    tmp_x = []
    for x in section:
        if shortAndAscii(x):
            tmp_x.append(x)
    return tmp_x

def removeNonAscii(page):
    page["title"] = check_and_remove_non_ascii(page["title"])
    page["infobox"] = check_and_remove_non_ascii(page["infobox"])
    page["categories"] = check_and_remove_non_ascii(page["categories"])
    page["external_links"] = check_and_remove_non_ascii(page["external_links"])
    page["references"] = check_and_remove_non_ascii(page["references"])
    page["body"] = check_and_remove_non_ascii(page["body"])

    return page

def caseunfold(page):
    # global initial_unique_tokens

    page["title"] = [x.lower() for x in page["title"]]
    page["infobox"] = [x.lower() for x in page["infobox"]]
    page["categories"] = [x.lower() for x in page["categories"]]
    page["external_links"] = [x.lower() for x in page["external_links"]]
    page["references"] = [x.lower() for x in page["references"]]
    page["body"] = [x.lower() for x in page["body"]]

    # for x in page["title"]:
    #     initial_unique_tokens.add(x)
    # for x in page["infobox"]:
    #     initial_unique_tokens.add(x)
    # for x in page["categories"]:
    #     initial_unique_tokens.add(x)
    # for x in page["external_links"]:
    #     initial_unique_tokens.add(x)
    # for x in page["references"]:
    #     initial_unique_tokens.add(x)
    # for x in page["body"]:
    #     initial_unique_tokens.add(x)

    # print("\n---------------------------------------------------\n")
    # print(page)
    # print("\n---------------------------------------------------\n")
    return page

citation_words = ["cite", "web", "url", "title", "author", "date", "website", "publisher", "access", "journal", "last1", "first1", "last2", "first2", "year", "title", "journal", "volume", "issue", "pages", "publisher", "doi", "url", "book", "last", "first", "link", "series", "year", "isbn", "coauthors", "editor", "trans", "edition", "location", "page", "chapter", "name"]
html_words = ["ref", "small", "align", "imag", "image", "center", "style", "flagicon", "nbsp", "jpg", "type", "\"", ":", "[", "]", ".", "(", ")", "-", ",", "'", ";", "?"]

def sanitizeStop(vec, type_vec):
    global stopedwords
    global citation_words
    global html_words
    global freq_count
    x = []
    stopers = ['|']
    for word in vec:
        if word not in stopers:
            if word in freq_count:
                freq_count[word]+=1
            else:
                freq_count[word]=1
            x.append(word)
    return x

def removeStopWords(page):
    # print(page["title"])
    # page["title"] = [word for word in page["title"] if not word in stopwords.words('english')]
    # print(x)
    # page["title"] = x
    # page["infobox"] = [word for word in page["infobox"] if not word in stopwords.words('english')]
    
    # page["title"] = x
    # page["categories"] = [word for word in page["categories"] if not word in stopwords.words('english')]
    # page["title"] = x
    # page["external_links"] = [word for word in page["external_links"] if not word in stopwords.words('english')]
    # page["title"] = x
    # page["references"] = [word for word in page["references"] if not word in stopwords.words('english')]
    # page["title"] = x
    # page["body"] = [word for word in page["body"] if not word in stopwords.words('english')]


    page["title"] = sanitizeStop(page["title"], "title")
    page["infobox"] = sanitizeStop(page["infobox"], "infobox")
    page["categories"] = sanitizeStop(page["categories"], "categories")
    page["external_links"] = sanitizeStop(page["external_links"], "external_links")
    page["references"] = sanitizeStop(page["references"], "references")
    page["body"] = sanitizeStop(page["body"], "body")
    return page

snow_stemmer = SnowballStemmer(language='english')

def get_stem_or_lemma(vec):
    z = []
    for x in vec:
        z.append(stemmer.stemWord(x))
        # z.append(snow_stemmer.stem(x))
    return z

def stem_and_lemma(page):
    page["title"] = get_stem_or_lemma(page["title"])
    page["infobox"] = get_stem_or_lemma(page["infobox"])
    page["categories"] = get_stem_or_lemma(page["categories"])
    page["external_links"] = get_stem_or_lemma(page["external_links"])
    page["references"] = get_stem_or_lemma(page["references"])
    page["body"] = get_stem_or_lemma(page["body"])
    return page


def inverted_index_creation(page):
    # print(page)
    # print("------------------------")
    global invidx

    title = Counter(page["title"])
    info = {}
    for x, val in title.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][TITLE] = val
    

    infobox = Counter(page["infobox"])
    for x, val in infobox.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][INFOBOX] = val
    

    body = Counter(page["body"])
    for x, val in body.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][BODY] = val
    

    categories = Counter(page["categories"])
    for x, val in categories.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][CATEGORY] = val
    

    external_links = Counter(page["external_links"])
    for x, val in external_links.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][LINKS] = val
    

    references = Counter(page["references"])
    for x, val in references.items():
        if x not in info:
            info[x] = [page["id"], 0, 0, 0, 0, 0, 0]
        info[x][REFERENCES] = val

    # for x, infolist in info.items():
    #     plain = sum(infolist[1:PLAIN])
    #     info[x][PLAIN] = plain
    
    for x, infolist in info.items():
        if x not in invidx:
            invidx[x] = []
        invidx[x].append(infolist)
    

    
    # if page["id"] == 4:
    #     print(info)
    #     exit()

cnt_of_tokens = 0

def encodeN(n,N,D="0123456789qwertyuiopasdfghjklzxc"):
    return (encodeN(n//N,N)+D[n%N]).lstrip("0") if n>0 else "0"

def decodeN(inputValue):
    tmap = str.maketrans('qwertyuiopasdfghjklzxc', 'abcdefghijklmnopqrstuv')
    result = int(inputValue.translate(tmap), 32)


def clean_index():
    global path_to_index
    global cnt_of_tokens
    global invidx
    freq = []
    # for x, vec in invidx.items():
    #     i = len(vec) - 1
    #     cnt = vec[i][-1]
    #     while(i > 0):
    #         vec[i][0] = vec[i][0] - vec[i-1][0]
    #         i = i - 1
    #         cnt += vec[i][-1]
    #     invidx[x] = vec

        # freq.append((cnt, x))



    #Removing
    output = ""
    for x, vec in sorted(invidx.items()):
        cnt_of_tokens += 1
        output += x + "|"
        for ve in vec:
            # output += "a"+str(ve[0])
            # output += str(hex(ve[0]))
            output += encodeN(ve[0], 32) + "."
            if ve[TITLE] > 0:
                output += "t"+str(ve[TITLE])
            if ve[INFOBOX] > 0:
                output += "i"+str(ve[INFOBOX])
            if ve[BODY] > 0:
                output += "b"+str(ve[BODY])
            if ve[CATEGORY] > 0:
                output += "c"+str(ve[CATEGORY])
            if ve[LINKS] > 0:
                output += "l"+str(ve[LINKS])
            if ve[REFERENCES] > 0:
                output += "r"+str(ve[REFERENCES])
            # if ve[PLAIN] > 0:
            #     output += "p"+str(ve[PLAIN])
            if ve != vec[-1]:
                output += "|"
        output += "\n"
    # print(output)

    file = open(path_to_index, 'w')
    file.write(output)
    file.close()
    invidx.clear()
    gc.collect()
    # freq.sort()
    # print(freq)

total_current_block_count = 0
cnt_block = 0
folder_name = "out_ben/"
def processPage(page):
    global freq_count
    global folder_name
    global total_current_block_count
    global path_to_index
    global cnt_block
    global invidx
    global start
    
    total_current_block_count += 1
    # if page["id"] > 6:
    #     freq_count = {k: v for k, v in sorted(freq_count.items(), key=lambda item: item[1])}
    #     fd = open("freq_count.txt", "w")
    #     for k, v in freq_count.items():
    #         tmp = k + " " + str(v) + "\n"
    #         fd.write(tmp)
    #     fd.close()
    #     exit()
    #     pass
    parsedPage = parsePage(page)
    parsedPage = tokenizePage(parsedPage)
    # return
    # parsedPage = removeNonAscii(parsedPage)
    # parsedPage = caseunfold(parsedPage)
    parsedPage = removeStopWords(parsedPage)
    # parsedPage = stem_and_lemma(parsedPage)

    inverted_index_creation(parsedPage)

    BLOCK_LIM = 300000
    if total_current_block_count % 10000 == 0:
        print(f"Cur count: {total_current_block_count}")
        print(timedelta(seconds=timer()-start))
    if total_current_block_count == BLOCK_LIM:
        cnt_block += 1
        total_current_block_count = 0
        clean_index()
        path_to_index = folder_name +str(cnt_block)
        invidx = {}
        end = timer()
        print(f"block done: {cnt_block}")
        print(timedelta(seconds=end-start))
        # if cnt_block == 4:
        #     exit()


    
def parseWikiDump():
    global path_to_dump

    events = ("start", "end")
    title = None
    page = {}
    id = 1
    page["id"] = id
    for event, elem in ET.iterparse(path_to_dump, events=events):
        t_name = strip_tag_name(elem.tag)
        # if t_name == "text":
        #     print(elem.text)
        #     print("\n\n\n---------------\n\n\n")
        #     # break
        # break
        if event == 'end':
            if t_name == "title":
                page["title"] = elem.text
            elif t_name == "text":
                page["text"] = elem.text
            elif t_name == "page":
                processPage(page)
                page = {}
                id = id + 1
                page["id"] = id
                if id == 5:
                    # break
                    pass
            elem.clear()



if __name__ == "__main__":
    folder_name
    # global isnvidx
    # print("Hello World!")
    # x = nltk.word_tokenize("Hello, namaste.... How are you?")
    # print(x)
    # print(stopwords.words('english'))

    start = timer()

    # print(len(sys.argv))

    path_to_dump = sys.argv[1]
    path_to_index = sys.argv[2]
    path_to_stats = sys.argv[3]

    path_to_index = folder_name + "0"

    if os.path.isfile(path_to_dump) is False:
        print("your path to dump don't exist, recheck before giving it.")
    

    # exit()
    parseWikiDump()
    freq_count = {k: v for k, v in sorted(freq_count.items(), key=lambda item: item[1])}
    fdo = open("freq_count_1.txt", "w")
    for k, v in freq_count.items():
        tmp = k + " " + str(v) + "\n"   
        fdo.write(tmp)
    fdo.close()
    # print("+++++++++++++++")
    # print(DA)
    # print(len(initial_unique_tokens))

    # check_lemmatization = set()
    # check_stemming = set()
    # check_stemmer = set()

    # sno = nltk.stem.SnowballStemmer('english')

    # for x in initial_unique_tokens:
    #     check_stemming.add(sno.stem(x))

    # lemma = nltk.wordnet.WordNetLemmatizer()
    # for x in initial_unique_tokens:
    #     check_lemmatization.add(lemma.lemmatize(x))

    # # print(len(check_stemming))
    # print(len(check_lemmatization))

    # total_len = 0
    # for x in initial_unique_tokens:
    #     check_stemmer.add(stemmer.stemWord(x))
    #     total_len += len(x)
    # print(len(check_stemmer))
    # print(total_len)
    # print(f"Total length = {total_len}")

    # print(initial_unique_tokens)

    clean_index()

    # print("--------------------")
    # print(cnt_of_tokens)
    # print(invidx)



    file = open(path_to_stats, 'w')
    file.write(str(len(initial_unique_tokens)) + "\n")
    file.write(str(cnt_of_tokens))
    file.close()

    end = timer()
    print(timedelta(seconds=end-start))

