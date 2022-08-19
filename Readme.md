# Wikipedia Search Engine
A simple search engine built in python capable of building optimised positional index for the Wikipedia dump & perform field queries.

## Data

The English data was taken from the Wikipedia corpus([link](https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml.bz2)). The Bengali data can be found ([here](https://dumps.wikimedia.org/bnwiki/20210720/bnwiki-20210720-pages-articles-multistream.xml.bz2)).

## Features
- Implements tf-idf based search algorithm over Wikipedia to return relevant results based on provided queries.
- Support for Field Queries . Fields include Title, Infobox, Body, Category, Links, and References of a Wikipedia page. This helps when a user is interested in searching for the cricketer ‘Virat Kohli’ where he would like to see the page containing the word ‘Kohli’ in the title and the word ‘RCB’ in the Infobox. You can store field type along with the word when you index.
- Have done the project for an Indian language(Bengali) as well. The readme for that is in the directory named `ben`.
- Created index size is 20GB which is 1/4th the size of the whole index.
- Search results are returned with 5 seconds based on the algorithm.

## How to run code

### Index creation

```bash
python main.py <path to dump>
mkdir out8
mkdir mini1
python merge.py
python create_title_index.py
python title_num_proper.py

```

### Searching

Create `queries.txt` if not already created.

```bash
python search.py queries.txt
```

Search results will get saved in the file named `queries_op.txt` in the same directory.

### Functionality of each code file

`main.py` creates mutlple mini indices in the directory `out8`. There are merged together to create 1460 small indices in the folder mini1. The `merge.py` is reponsible for this.

`create_title_index.py` and `title_num_proper.py` create two files, `title_b32.txt` and `titles.txt`

`titles.txt` contains the titles of documents, one per line.

`title_b32.txt` contains the seek location of each document in the titles file. The seek location for any document can be found in constant time, because the seek is stored in a field of **length 6** per line in the `title_b32.txt`. The seek location is encoded in **base32** to save space.


Made with ❤️️ as part of Information Retrieval & Extraction course, Monsoon 2020, IIIT Hyderabad.
