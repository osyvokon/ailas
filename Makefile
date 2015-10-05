all: node
	node index.js &
	./server.py
	kill %1

node:
	npm install
