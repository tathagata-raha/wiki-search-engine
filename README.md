# wiki-search-engine

A simple search engine built in python capable of building optimised positional index for the Wikipedia dump & perform field queries. This was built as a part of IRE course under Dr. Vasudeva Varma.

## Data

Data was taken from the Wikipedia corpus([link](https://drive.google.com/file/d/1QMpM1CSn6j8Hwu5AabTqTQ1km9xCzSEV/view?usp=sharing)).

## Features
- Support for Field Queries . Fields include Title, Infobox, Body, Category, Links, and References of a Wikipedia page. This helps when a user is interested in searching for the cricketer ‘Virat Kohli’ where he would like to see the page containing the word ‘Kohli’ in the title and the word ‘RCB’ in the Infobox. You can store field type along with the word when you index.
- Index size should be less than 1⁄4 of dump size.
- Relevant queries are returned within 5 sec.

## Running the indexer
To run the indexer, run `bash index.sh <path_to_wiki_dump> <path_to_invertedindex_output> <invertedindex_stat.txt>`.

## Constructing the index.
- BasicStages(inorder):
- XML parsing: SAX parser used
- Data preprocessing : NLTK used
  - Tokenization
  - Case folding
  - Stop words removal
  - Stemming
- Posting List / Inverted Index Creation
- Optimize

## Searching the query
To search a query, run `bash search.sh inverted_index/ query_string`

