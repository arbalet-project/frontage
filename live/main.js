// Modules to control application life and create native browser window
const path = require('path');
const ipParser = require('ip6addr');
const express = require('express');
const expressServer = express();
const http = require('http').Server(expressServer);
const port = 3000;
const io = require('socket.io')(http); //socket
const redis = require('redis');
const amqp = require('amqplib/callback_api');

let redisClient = redis.createClient(6379, 'redis');
let rabbitPublisher;
let clientsLogged = new Map();
let userlist = new Array();
let grantedUser = {'id':'turnoff', 'login':'turnoff'};
let frontageConnected = false;

function initServer() {

  // Init the session system
  let session = require('express-session')({
    secret: 'my-secret',
    resave: true,
    saveUninitialized: true
  });

  let sharedsession = require('express-socket.io-session');
  expressServer.use(session);
  io.use(sharedsession(session, {
    autoSave: true
  }));
  // Routes
  expressServer.get('/blocklyLanguage',function(req,res){
      res.sendFile(__dirname + '/public/blockly/msg/js/fr.js');
  })
  expressServer.use(express.static( __dirname + '/public'));
  expressServer.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist'));

  // Start the express server
  http.listen(port, function () {
    console.log('Server listening on ' + port);
  });
}

/**
 * Define the behaviour of sockets and the different messages the server can handle
 */
function initSocket() {
  // Define the events to listen on a new socket
  io.on('connection', function (socket) {
    // If the user is already logged in we send him/her the related informations
    if(clientsLogged.has(socket.handshake.session.id)){
      let client = clientsLogged.get(socket.handshake.session.id);
      socket.emit('logged',{name: client.login, ip: client.ip});
      client.socket = socket;
      client.status = "connected";
      clientsLogged.set(socket.handshake.session.id, client);
      for (var c of clientsLogged.values()){
        let user = {"id": c.id, "username": c.login};
        userlist.push(user);
      }
      // post userlist on redis
      console.log(userlist);
      redisClient.set('KEY_USERS', JSON.stringify({'users': userlist}), function(err, reply) { console.log(err);});
      if(client == grantedUser){
        socket.emit('granted');
      }
    }

    // When the user logs in (enter his/her name)
    socket.on('login', function (login) {
      if (!clientsLogged.has(socket.handshake.session.id)) {
        clientsLogged.set(socket.handshake.session.id, {
          socket: socket,
          id: socket.handshake.session.id,
          login: login,
          status: "connected",
          ip: getIPV4(socket.handshake.address)
        });
        userlist.push({"id": socket.handshake.session.id, "username": login});
        // post userlist on redis
        console.log(userlist);
        redisClient.set('KEY_USERS', JSON.stringify({'users': userlist}), function(err, reply) { console.log(err);});
        let client = clientsLogged.get(socket.handshake.session.id);
        socket.emit('logged', {name: client.login, ip: client.ip});
      }
    });

    socket.on('disconnect', function() {
      if (clientsLogged.has(socket.handshake.session.id)) {
        let client = clientsLogged.get(socket.handshake.session.id);
        client.status = "disconnected";
        clientsLogged.set(socket.handshake.session.id, client);
        console.log('Client disco');
        let nuserlist = new Array();
        for (var user of userlist){
          if (user.id != client.id){
            nuserlist.push(user);
          }
        }
        userlist = nuserlist;
        //post userlist on redis
        console.log(userlist);
        redisClient.set('KEY_USERS', JSON.stringify({'users': userlist}), function(err, reply) { console.log(err);});
      }
    });

    socket.on('updateGrid',function(pixelsToUpdate){
      if(boardConnected && (grantedUser === clientsLogged.get(socket.handshake.session.id) )){
        //post pixelsToUpdate on RabbitMQ
        let msg = JSON.stringify({'pixels': pixelsToUpdate});
        rabbitPublisher.publish('logs', '', Buffer.from(msg));
        console.log(" [x] Sent %s", msg);
      }
    });
  });
}
/**
 * Define the events messages received by the rendering JS process
 */
function grant(user) {
  if (user['id'] != 'turnoff') {
    clientsLogged.get(user['id']).socket.emit('granted');
  }
  // ipcMain.on('grantUser', function (event, arg) {
  //   grantedUser = clientsLogged.get(arg);
  //   grantedUser.socket.emit('granted');
  //   grantedUser.socket.broadcast.emit('ungranted');
  //
  // });
}

function ungrant(user){
  if (user['id'] != 'turnoff') {
    clientsLogged.get(user['id']).socket.emit('ungranted');
  }
  // ipcMain.on('ungrantUser', function(event,arg){
    //   clientsLogged.get(arg).socket.emit('ungranted');
    //   grantedUser = '';
    // });
}

function updateValues(){
  // may be useless
  let previousFrontageStatus = false;
  redisClient.get('KEY_FRONTAGE_IS_UP', function(err, reply) {
    previousFrontageStatus = frontageConnected;
    frontageConnected = (reply['isup'] == 'True')? true : false;
    if (previousFrontageStatus != frontageConnected){
      if (frontageConnected){
        // TO DO
        //start publisher
      }
    }
  });
  redisClient.get('KEY_GRANTED_USER', function(err, reply) {
    let newGranted = JSON.parse(reply);
    if (newGranted['id'] != grantedUser['id']){
      ungrant(grantedUser);
      grant(newGranted);
      grantedUser = newGranted;
    }
  });
}

function initFappInteraction(){
  redisClient.set('KEY_GRANTED_USER', JSON.stringify(grantedUser)); // init redis DB
  redisClient.set('KEY_FRONTAGE_IS_UP', 'False');
}

/**
 * Format the given ip adress to the ipv4 format
 * @param {Object} ip
 * @returns {String} The formated ip
 */
function getIPV4(ip) {
  if (ip == '::1') {
    return '127.0.0.1';
  } else {
    return ipParser.parse(ip).toString({
      format: 'v4'
    });
  }
}

// main
const opt = { credentials: require('amqplib').credentials.plain('frontage', 'uHm65hK6]yfabDwUUksqeFDbOu') };
amqp.connect('amqp://rabbit', opt, function(error0, connection) {
  if (error0) {
    throw error0;
  }
  connection.createChannel(function(error1, channel) {
    if (error1) {
      throw error1;
    }
    channel.assertExchange('logs', 'fanout', {
      durable: false
    });
    rabbitPublisher = channel;
  });
});

initServer();
initSocket();
initFappInteraction();

// update granted user and rabbitmq publisher state each 1000ms
 setInterval(updateValues, 1000);
