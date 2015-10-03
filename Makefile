all: corpora/warpeace.txt node
	node index.js &
	./server.py
	kill %1

node:
	npm install

corpora/warpeace.txt:
	wget http://www.gutenberg.org/cache/epub/2600/pg2600.txt -O corpora/warpeace.txt
