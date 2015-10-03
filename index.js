var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var moment = require('moment');

app.get('/', function(req,res){
	res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  socket.on('chat message', function(msg){
    console.log(msg);
    //var time = moment().format('MMMM Do YYYY, h:mm:ss a');
    var time = moment().format('h:mm:ss a');
    io.emit('chat message', msg + " - " + time);
  });
});

http.listen(3001, function(){
	console.log('listening on *:3001');
});
