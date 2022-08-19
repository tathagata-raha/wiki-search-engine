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
import io
import heapq    
from heapq import heapify, heappush, heappop

print (io.DEFAULT_BUFFER_SIZE)


global start
heap = []
# last_index_val = 213
last_index_val = 213
fd = {} # Dictionary of file descriptors
line = {} # one line of each file
doc_list = {} # doc.b1r1.. values
current_token = ""
current_line_to_write = ""
current_file_to_write = ""
current_file_content = ""

def encodeN(n,N,D="0123456789qwertyuiopasdfghjklzxc"):
    return (encodeN(n//N,N)+D[n%N]).lstrip("0") if n>0 else "0"

def decodeN(inputValue):
    tmap = str.maketrans('qwertyuiopasdfghjklzxc', 'abcdefghijklmnopqrstuv')
    result = int(inputValue.translate(tmap), 32)
    return result

# print(encodeN(0, 32))
# print(decodeN(encodeN(0, 32)))

def collect_file_descriptors():
    global fd
    for i in range(last_index_val+1):
        try:
            fd[i] = open("out8/"+str(i), "r", 64 * 1024)
        except IOError as e:
            print ("Cannot open file: %s" % e.strerror)
            break

def get_token_from_line(line_str):
    st = re.compile('[^|]+\|')
    m = st.match(line_str)
    return line_str[:m.end()-1]

def initialize_heap():
    global line
    global fd
    global heap
    global last_index_val

    for i in range(last_index_val+1):
        line[i] = fd[i].readline().strip().split("|")
        if line[i]:
            heapq.heappush(heap, (line[i][0], i))

def get_file_name(token):
    lenn = 2
    return token[:lenn]

docs_list = []
out_file = None

def write_to_file(file):
    global line
    global start
    global fd
    global heap
    global last_index_val
    global current_token
    global current_line_to_write
    global current_file_to_write
    global current_file_content
    file = "./mini1/"+file
    # with open(file, "w") as f:
    #     f.write(str)
    #     print("write to file: ", file)
    print(timedelta(seconds=timer()-start))
    file = open(file, 'w')
    file.write(current_file_content)
    file.close()
    print("write to file: ", file)
    print(timedelta(seconds=timer()-start))

def process_least_token(tok):
    global line
    global fd
    global heap
    global last_index_val
    global current_token
    global current_line_to_write
    global current_file_to_write
    global current_file_content
    global docs_list
    global out_file

    token = tok[0]
    indid = tok[1]

    new_file = get_file_name(token)
    # if new_file == "bd":
    #     print(token)
    if new_file != current_file_to_write:
        if out_file:
            out_file.close()
        current_file_to_write = new_file

        out_file = open(f"./mini1/{current_file_to_write}.txt", "w")
        print("Writing to file: ", current_file_to_write)
    docs_list = []
    docs_list.extend(line[indid][1:])
    
    line[indid] = fd[indid].readline().strip()
    if line[indid]:
        line[indid] = line[indid].split("|")
        heapq.heappush(heap, (line[indid][0], indid))

    while heap and heap[0][0] == token:
        old_file = heapq.heappop(heap)
        file_id = old_file[1]
        docs_list.extend(line[file_id][1:])
        line[file_id] = fd[file_id].readline().strip()
        if line[file_id]:
            line[file_id] = line[file_id].split("|")
            heapq.heappush(heap, (line[file_id][0], file_id))
    
    final_line = token + "|" + '|'.join(docs_list) + "\n"
    if out_file:
        out_file.write(final_line)
    # if current_token == token:
    #     current_line_to_write += line[indid][len(token):-1]
    #     # print(line[indid])
    #     # print(line[indid][len(token):-1])
    #     # print("OVER")
    #     # exit()
    # else:
    #     if current_token and not newFile:
    #         current_file_content += current_line_to_write + "\n"
    #     current_line_to_write = line[indid][:-1]
    #     current_token = token

    # line[indid] = fd[indid].readline().strip().split("|")
    # if line[indid]:
    #     heapq.heappush(heap, (line[indid][0], indid))

def start_processing_tokens():
    global line
    global fd
    global heap
    global last_index_val
    while len(heap) > 0:
        x = heapq.heappop(heap)
        process_least_token(x)
    

if __name__ == "__main__":
    collect_file_descriptors()

    start = timer()

    initialize_heap()
    start_processing_tokens()
    # heapq.heappush(heap, ("zonal", 10))
    # heapq.heappush(heap, ("zonal", 12))
    # heapq.heappush(heap, ("zonal", 3))
    # heapq.heappush(heap, ("are", 10))
    # heapq.heappush(heap, ("bre", 10))
    # heapq.heappush(heap, ("bre", 10))
    # heapq.heappush(heap, ("bre", 10))
    # heapq.heappush(heap, ("bre", 2))
    # heapq.heappush(heap, ("bre", 3))
    # heapq.heappush(heap, ("bre", 4))
    # heapq.heappush(heap, ("bre", -1))
    # heapq.heappush(heap, ("bre", 2))
    # heapq.heappush(heap, ("bre", 0))
    # heapq.heappush(heap, ("bre", 0))
    # heapq.heappush(heap, ("0-9", 0))
    # heapq.heappush(heap, ("0-6-4", 0))

    # printing the elements of the heap

    

    end = timer()
    print(timedelta(seconds=end-start))
    pass
