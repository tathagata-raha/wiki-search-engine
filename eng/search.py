import nltk
import re
import xml.etree.ElementTree as ET
import Stemmer
from nltk import parse
from nltk.corpus import stopwords
from collections import Counter
import sys
import os, json

from multiprocessing import Pool

from timeit import default_timer as timer
from datetime import timedelta
import math

path_to_index = ""
query = ""
queries_op = None
query_result = {}
parsed_tokens = {}

TITLE = 0
INFOBOX = 1
BODY = 2
CATEGORY = 3
LINKS = 4
REFERENCES = 5


field_value = {
    "t": 0,
    "i": 1,
    "b": 2,
    "c": 3,
    "l": 4,
    "r": 5
}

field_num = {
    "t": TITLE,
    "i": INFOBOX,
    "b": BODY,
    "c": CATEGORY,
    "l": LINKS,
    "r": REFERENCES
}

default_field_values = [2, 2, 1, 3, 2, 2]

query_file = None
start = 0



def encodeN(n,N,D="0123456789qwertyuiopasdfghjklzxc"):
    return (encodeN(n//N,N)+D[n%N]).lstrip("0") if n>0 else "0"

def decodeN(inputValue):
    tmap = str.maketrans('qwertyuiopasdfghjklzxc', 'abcdefghijklmnopqrstuv')
    result = int(inputValue.translate(tmap), 32)
    return result

def get_file_name(token):
    lenn = 2
    return token[:lenn] + ".txt"

def find_stat(tok, doc_id=0):
    match = re.search('(\d+)', tok)
    # if not match:
    #     return
    # print(match.group())
    zz = tok.split(".")
    ret = {
        "id": decodeN(zz[0]),
        "t": 0,
        "i": 0,
        "b": 0,
        "c": 0,
        "l": 0,
        "r": 0
    }
    tok = zz[1]
    # tok = tok[match.end():]
    # print(tok)
    match = re.search('[tibclrp]', tok)
    while match is not None and tok != "":
        # print(match.group())
        tok = tok[match.end():]
        match1 = re.search('(\d+)', tok)
        # print(match1.group())
        ret[match.group()] = int(match1.group())
        tok = tok[match1.end():]
        match = re.search('[tibclrp]', tok)
        # print(match)
    # print(ret)
    return ret

def get_info_from_line(line_no):
    global lines
    x = lines[line_no]
    st = re.compile('[^|]+\|')
    m = st.match(x)
    y = x[m.end():-1]
    z = y.split("|")

    q_result = {
        "title": [],
        "infobox": [],
        "body": [],
        "category": [],
        "links": [],
        "reference": []
    }
    # print(z)
    # Keep doc_id in check
    docID = 0
    for doc in z:
        # print(doc)
        ret = find_stat(doc, docID)
        docID = ret["id"]

        if ret["t"] > 0:
            q_result["title"].append(docID)
        if ret["i"] > 0:
            q_result["infobox"].append(docID)
        if ret["b"] > 0:
            q_result["body"].append(docID)
        if ret["c"] > 0:
            q_result["category"].append(docID)
        if ret["l"] > 0:
            q_result["links"].append(docID)
        if ret["r"] > 0:
            q_result["reference"].append(docID)

    return q_result

    

def set_index():
    global path_to_index
    global lines
    file = open(path_to_index, 'r')
    lines = file.readlines()
    file.close()
    return
    # print(lines[109749])
    # x = lines[109749]
    # st = re.compile('[^|]+\|')
    # m = st.match(x)
    # print(m.group()[:-1])

    # print(x[m.end():])
    # y = x[m.end():-1]
    # print(y.split("|"))
    # z = y.split("|")
    # s = find_stat(z[-2])
    # print(s)




# Algorithm:
# 0. Find the element to search by preprocessing.
# 1. Find the line using binary search.
# 2. Iterate through all articles and add it to a dict containing list as required.


def get_token(line_no):
    global lines
    st = re.compile('[^|]+\|')
    m = st.match(lines[line_no])
    # print(m.group()[:-1])
    return m.group()[:-1]


def search_index(query):
    global lines
    lo = 0
    hi = len(lines) - 1
    # print(lo, hi)
    answer = -1
    # print("Query Here: ", query)
    while lo <= hi:
        mid = (lo + hi) // 2
        # print(lo, mid, hi)
        mid_x = get_token(mid)
        if mid_x == query:
            answer = mid
            # print("ANSWER")
            break
        if query < mid_x:
            hi = mid-1
        else:
            lo = mid+1
    if answer == -1:
        # Return empty
        empt = {
            "title": [],
            "infobox": [],
            "body": [],
            "category": [],
            "links": [],
            "reference": []
        }
        return empt
        pass
    # print(answer)
    return get_info_from_line(answer)
    
    # exit()
    pass


def get_stem_or_lemma(vec):
    stemmer = Stemmer.Stemmer('english')
    stemmer.maxCacheSize = 1000000
    z = []
    for x in vec:
        z.append(stemmer.stemWord(x))
    return z


def process_query(query, field_type):
    global query_result
    global parsed_tokens
    global field_value
    global field_num
    global default_field_values
    # print("Query: ", query)
    # print(parsed_tokens)
    # print(field_type)
    # Do everything we do tokens
    pattern = r'''(?x)          # set flag to allow verbose regexps
        (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
      | \w+(?:-\w+)*        # words with optional internal hyphens
      | \d+  # currency and percentages, e.g. $12.40, 82%
    '''
    queries = nltk.regexp_tokenize(query, pattern)
    queries = [x.lower() for x in queries]
    # print(queries)
    queries_before_stemming = queries
    queries = get_stem_or_lemma(queries)
    # print(queries)
    for tok in queries:
        if tok in parsed_tokens and field_type != "p":
            if parsed_tokens[tok][field_num[field_type]] < default_field_values[0]+0.1:
                parsed_tokens[tok][field_num[field_type]] *= 5
            pass
        else:
            parsed_tokens[tok] = [x for x in default_field_values]
            if field_type != "p":
                parsed_tokens[tok][field_num[field_type]] *= 5
            else:
                # parsed_tokens[tok] = [20, 2, 1, 2, 1, 1]
                parsed_tokens[tok] = [10, 3, 1, 3, 2, 2]
                # [8, 2, 1, 3, 2, 2]
                pass


def parse_query(query):
    global parsed_tokens
    # print("-------------------------------")
    # print(parsed_tokens)
    # print("-------------------------------")
    match = re.search('[tibclr]:', query)
    if match is None:
        process_query(query, "p")
        # print(parsed_tokens)
        # parsed_tokens = {}
        return
    if match.start() > 0:
        process_query(query[:match.start()], "p")
        query = query[match.start():]
        match = re.search('[tibclr]:', query)
    
    while match is not None and query != "":
        # print(query[match.end():])
        # print("-----")
        # print(query)
        match_type = query[match.start():match.end()-1]
        # print(match)
        # print(match_type)
        query = query[match.end():]
        match = re.search('[tibclr]:', query)
        if match is None:
            # print(query)
            # print("Q: ", query, match_type)
            process_query(query, match_type)
            break
        q1 = query[:match.start()]
        # print(match)
        process_query(q1, match_type)
        # print("Query: ", q1)\

def read_token_list(file_name, token):
    if os.path.isfile(file_name) == False:
        return []
    st = re.compile('[^|]+\|')
    with open(file_name) as fd:
        x = fd.readline()
        while x:
            m = st.match(x)
            tok = x[:m.end()-1]
            # print(tok, token)
            # print(len(tok), len(token))
            if tok == token:
                # print(x)
                # print("HOHO")
                return x.strip().split("|")[1:]
            x = fd.readline()
    return ""

def find_stat(tok):
    ret = {
        "t": 0,
        "i": 0,
        "b": 0,
        "c": 0,
        "l": 0,
        "r": 0
    }
    if not tok:
        return ret
    key = tok[0]
    if not tok:
        return ret
    p_list = ["t", "i", "b", "c","l", "r"]
    so_far = ""
    for x in tok:
        if x in p_list:
            if so_far:
                ret[key] = int(so_far)
            so_far = ""
            key = x
        else:
            so_far += x
    ret[key] = int(so_far)
    return ret

    # match = re.search('[tibclr]', tok)
    # while match is not None and tok != "":
    #     # print(match.group())
    #     tok = tok[match.end():]
    #     match1 = re.search('(\d+)', tok)
    #     # print(match1.group())
    #     ret[match.group()] = int(match1.group())
    #     tok = tok[match1.end():]
    #     match = re.search('[tibclrp]', tok)
    #     # print(match)
    # # print(ret)
    # return ret

def find_tfidf_postings(query_token):
    ret_dict = {}
    token = query_token[0]
    mult = query_token[1]
    file_to_find = get_file_name(token)
    file_to_find = "mini1/"+file_to_find
    # print("///////////////////////////////")
    # print(query_token)
    st = timer()
    tok_list = read_token_list(file_to_find, token)
    if len(tok_list) == 0:
        return ret_dict
    # print(len(tok_list))
    # print(f"////////////////\n{query_token[0]} {len(tok_list)} {timedelta(seconds=timer()-st)}")
    # print(tok_list)
    # Finding the tf-idf score
    n_t = len(tok_list)
    N = 21384756
    idf = math.log(N/n_t)

    # print("Tokens: ", query_token, n_t)

    for tok in tok_list:
        tok = tok.split('.')

        docid = "0"
        stat = {
            "t": 0,
            "i": 0,
            "b": 0,
            "c": 0,
            "l": 0,
            "r": 0
        }
        sto = timer()
        # print("==")
        # print(timedelta(seconds=timer()-sto))
        # docid = decodeN(tok[0])
        docid = tok[0]
        # print(timedelta(seconds=timer()-sto))
        stat = find_stat(tok[1])
        # print(timedelta(seconds=timer()-sto))
        score = 0
        if stat["t"] > 0:
            tfidf = math.log(1+stat["t"])*idf
            score += mult[TITLE] * tfidf
        if stat["i"] > 0:
            tfidf = math.log(1+stat["i"])*idf
            score += mult[INFOBOX] * tfidf
        if stat["b"] > 0:
            tfidf = math.log(1+stat["b"])*idf
            score += mult[BODY] * tfidf
        if stat["c"] > 0:
            tfidf = math.log(1+stat["c"])*idf
            score += mult[CATEGORY] * tfidf
        if stat["l"] > 0:
            tfidf = math.log(1+stat["l"])*idf
            score += mult[LINKS] * tfidf
        if stat["r"] > 0:
            tfidf = math.log(1+stat["r"])*idf
            score += mult[REFERENCES] * tfidf
        if score > 5.0:
            ret_dict[docid] = score
        # ret_dict[docid] = score
    # print(ret_dict)
    # print("XYZ")

    # print(f"////////////////\n{len(ret_dict.keys())}\n{query_token[0]} {len(tok_list)} {timedelta(seconds=timer()-st)}")
    return ret_dict
        
        

    pass

def get_doc_title(docid):
    seek_title = 0
    docid = decodeN(docid)
    with open("title_b32.txt") as fd:
        fd.seek((docid-1)*7)
        seek_title = decodeN(fd.readline())
    with open("titles.txt") as fd:
        fd.seek(seek_title)
        return fd.readline()


def print_titles(list_docs):
    # (score, docid format)
    for doc in list_docs:
        t = get_doc_title(doc[1]).strip()
        print(f"{decodeN(doc[1])}, {t}", file=queries_op)
    

def search_result():
    global parsed_tokens
    token_query = []
    for x, vec in sorted(parsed_tokens.items()):
        token_query.append((x, vec))
    # print(token_query)
    # return
    ans = {}
    # for que in token_query:
    #     x = find_tfidf_postings(que)
    #     for a, b in x.items():
    #         if a not in ans:
    #             ans[a] = b
    #         else:
    #             ans[a] = ans[a] + b
    
    p = Pool()
    results_d = p.map(find_tfidf_postings, token_query)
    p.close()
    p.join()
    for x in results_d:
        for a, b in x.items():
            if a not in ans:
                ans[a] = b
            else:
                ans[a] = ans[a] + b  

    # print(ans)
    list_docs = []
    for a, b in ans.items():
        list_docs.append((b, a))
    list_docs.sort(reverse=True)
    # print(list_docs[:10])
    print_titles(list_docs[:10])


if __name__ == "__main__":

    # x = read_token_list("mini1/0m.txt", "0m9ep")
    # print(x)
    # for y in x:
    #     y = y.split('.')
    #     z = y[1]
    #     print(z)
    #     print(find_stat(z))
    # exit()
    start = timer()
    input_file_name = sys.argv[1]
    if input_file_name == "":
        input_file_name = "queries.txt"
    query_file = open(input_file_name, "r")
    queries_op = open("queries_op.txt", "w")
    while True:
        # parsed_tokens.clear()
        start_q = timer()
        x = query_file.readline().strip()
        if not x:
            break
        parse_query(x)
        # print(parsed_tokens)
        # print("*******************************")
        search_result()
        parsed_tokens = {}
        time_taken = timedelta(seconds=timer()-start_q)
        print(f"{int(time_taken.seconds)}", file=queries_op)
        # print("---------------------------------------------")
        print("", file=queries_op)

    end = timer()
    print(timedelta(seconds=end-start))

    
