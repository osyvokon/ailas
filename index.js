var app = require('express')();
var http = require('http').Server(app);
var request = require('request');
var io = require('socket.io')(http);
var moment = require('moment');

//var API_URL = 'http://40.115.53.131:5000/api';
var API_URL = 'http://localhost:5000/api';


app.get('/', function(req,res){
	res.sendFile(__dirname + '/index.html');
});

app.get('/main.css', function(req,res){
	res.sendFile(__dirname + '/main.css');
});

io.on('connection', function(socket){
  window.scrollTo(0,document.body.scrollHeight);
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

    request.post(API_URL + '/session/test/say', {json: messageToClients},
      function (error, response, body) { 
        io.emit('chat message', {
          'person': 'bot',
          'txt': body && body.hint,
          'timestamp': moment().format('h:mm:ss a')
        });
      });
  });
});

http.listen(3001, function(){
	console.log('listening on *:3001');
});
