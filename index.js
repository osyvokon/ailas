var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var moment = require('moment');

app.get('/', function(req,res){
	res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  socket.on('chat message', function(msg){
    //var time = moment().format('MMMM Do YYYY, h:mm:ss a');
    var time = moment().format('h:mm:ss a');

    var messageToClients = {
    	'person': msg['person'],
    	'txt': msg['txt'],
    	'timestamp': time
	}
	console.log(messageToClients);
    io.emit('chat message', messageToClients);
  });
});

http.listen(3001, function(){
	console.log('listening on *:3001');
});
