var app = require('express')();
var http = require('http').Server(app);
var request = require('request');
var io = require('socket.io')(http);
var moment = require('moment');
var roomDict = {};
var people = {};

//var API_URL = 'http://40.115.53.131:5000/api';
var API_URL = 'http://localhost:5000/api';

var computeNamelist = function(intendedRoom) {
	var namelist = [];
	for (var socketIdKey in people) {
	  if (people.hasOwnProperty(socketIdKey)) {
	  	if (intendedRoom == people[socketIdKey].room) {
	  		namelist.push(people[socketIdKey].name);
	  	}
	  }
	}
	return namelist
}


app.get('/', function(req,res){
	console.log(req);
	res.sendFile(__dirname + '/index.html');
});

app.get('/rooms', function(req,res){
	var room_id = req.param('id');
	res.set('room_id', room_id)
	res.sendFile(__dirname + '/index.html');
	var messageToClients = {
    	'person': 'bot',
    	'txt': 'room_id is: ' + room_id,
    	'timestamp': '',
    	'room': room_id
	}
    io.emit('chat message', messageToClients);
});

app.get('/main.css', function(req,res){
	res.sendFile(__dirname + '/main.css');
});

io.on('connection', function(socket){

  // NODE SERVER GETS A CHAT MESSAGE
  // -------------------------------
  socket.on('chat message', function(msg){
    //var time = moment().format('MMMM Do YYYY, h:mm:ss a');
    var time = moment().format('h:mm:ss a');

    var messageToClients = {
    	'person': msg['person'],
    	'txt': msg['txt'],
    	'timestamp': time,
    	'room': msg['room']
	}
	console.log(messageToClients);
    io.emit('chat message', messageToClients);

    request.post(API_URL + '/session/test/say', {json: messageToClients},
      function (error, response, body) { 
        io.emit('chat message', {
          'person': 'bot',
          'txt': body && body.hint,
          'timestamp': moment().format('h:mm:ss a'),
          'room': msg['room']
        });
      });
  });

  // NODE SERVER GETS A JOIN MESSAGE
  // -------------------------------
  socket.on('join message', function(msg){
 	// Add user to dict
  	people[socket.id] = { 
  		'name': msg['person'], 
  		'room': msg['room']
  	}
  	var namelist = computeNamelist(msg['room']);
  	var messageToClients = {
    	'namelist': namelist,
    	'txt': msg['txt'],
    	'timestamp': '',
    	'room': msg['room']
	}
  	io.emit('join ack message', messageToClients);

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
			var temproom = people[socket.id].room;
			delete people[socket.id];
			//send new message to update clients
			var namelist = computeNamelist(temproom);
		  	var messageToClients = {
		    	'namelist': namelist,
		    	'txt': '',
		    	'timestamp': '',
		    	'room': temproom
			}
  			io.emit('join ack message', messageToClients);
		}
	});
});

http.listen(3001, function(){
	console.log('listening on *:3001');
});
