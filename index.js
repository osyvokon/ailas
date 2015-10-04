var app = require('express')();
var http = require('http').Server(app);
var request = require('request');
var io = require('socket.io')(http);
var moment = require('moment');
var people = {};

//var API_URL = 'http://40.115.53.131:5000/api';
var API_URL = 'http://localhost:5000/api';

var computeNamelist = function() {
	var namelist = [];
	for (var socketIdKey in people) {
	  if (people.hasOwnProperty(socketIdKey)) {
	    namelist.push(people[socketIdKey].name);
	  }
	}
	return namelist
}


app.get('/', function(req,res){
	res.sendFile(__dirname + '/index.html');
});

app.get('/main.css', function(req,res){
	res.sendFile(__dirname + '/main.css');
});

io.on('connection', function(socket){
  io.emit('chat message', {
    person: 'bot',
    txt: 'Known commands: \guess hints'
  });

  // NODE SERVER GETS A CHAT MESSAGE
  // -------------------------------
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

  // NODE SERVER GETS A JOIN MESSAGE
  // -------------------------------
  socket.on('join message', function(msg){
 	// Add user to dict
  	people[socket.id] = { 
  		'name': msg['person'] 
  	}
  	var namelist = computeNamelist();
  	io.emit('join ack message', namelist);

    // request.get(API_URL + '/session/test/scores',
    //   function (error, response, body) {
    //   	// Update scores
    //     //////////
    //   });
  });

  // NODE SERVER GETS A DISCONNECT MESSAGE
  // -------------------------------------
  socket.on("disconnect", function() {
		if (typeof people[socket.id] !== "undefined") { //this handles the refresh of the name screen
			console.log('disconnect: ' + people[socket.id].name);
			// Remove from people dict
			delete people[socket.id];
			//send new message to update clients
			var namelist = computeNamelist();
  			io.emit('join ack message', namelist);
		}
	});
});

http.listen(3001, function(){
	console.log('listening on *:3001');
});
