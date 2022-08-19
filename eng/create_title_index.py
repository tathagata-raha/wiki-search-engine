import xml.etree.ElementTree as ET
import sys
import os
from timeit import default_timer as timer
from datetime import timedelta

path_to_dump = ""

start = 0

def strip_tag_name(t):
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx+1:]
    return t

def encodeN(n,N,D="0123456789qwertyuiopasdfghjklzxc"):
    return (encodeN(n//N,N)+D[n%N]).lstrip("0") if n>0 else "0"

def decodeN(inputValue):
    tmap = str.maketrans('qwertyuiopasdfghjklzxc', 'abcdefghijklmnopqrstuv')
    result = int(inputValue.translate(tmap), 32)

out_file = None
seek_file = None

def parseWikiDump():
    global out_file
    global seek_file
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
        current_seek = 1
        if event == 'end':
            if t_name == "title":
                page["title"] = elem.text
                current_seek = out_file.tell()
                seek_file.write(str(current_seek)+"\n")
                out_file.write(elem.text+"\n")
                id = id + 1
            elem.clear()



if __name__ == "__main__":
    out_file = open("titles.txt", "w+")
    seek_file = open("title_seek.txt", "w+")

    start = timer()
    path_to_dump = sys.argv[1]

    if os.path.isfile(path_to_dump) is False:
        print("your path to dump don't exist, recheck before giving it.")

    parseWikiDump()

    end = timer()
    print(timedelta(seconds=end-start))

    out_file.close()
    seek_file.close()

