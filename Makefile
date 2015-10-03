all: corpora/warpeace.txt
	python server.py

corpora/warpeace.txt:
	wget http://www.gutenberg.org/cache/epub/2600/pg2600.txt -O corpora/warpeace.txt
