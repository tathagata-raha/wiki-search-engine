### How to run code

Make sure you are in the directory named `ben`.

#### Index creation

```bash
python main.py <path to dump>
mkdir out_ben
python create_title_index.py
python title_num_proper.py

```

#### Searching

Create `queries.txt`.

```bash
python search.py queries.txt
```

Search results will get saved in the file named `queries_op.txt` in the same directory.



#### Functionality of each code file

`main.py` creates an index

`create_title_index.py` and `title_num_proper.py` create two files, `title_b32.txt` and `titles.txt`

`titles.txt` contains the titles of documents, one per line.

`title_b32.txt` contains the seek location of each document in the titles file. The seek location for any document can be found in constant time, because the seek is stored in a field of **length 6** per line in the `title_b32.txt`. The seek location is encoded in **base32** to save space.
