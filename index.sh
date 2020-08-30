if [ -d "2018114017/index" ]
then
echo "Directory index exists."
else
mkdir 2018114017/index
echo "Creating index directory"
fi
python 2018114017/wiki_indexer.py $1 $2 $3
