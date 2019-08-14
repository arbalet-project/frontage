// Modules to control application life
const path = require('path');
const fs = require('fs');
const express = require('express');
const expressServer = express();
const http = require('http').Server(expressServer);
const port = 3000;
const io = require('socket.io')(http); //socket
const redis = require('redis');
const amqp = require('amqplib/callback_api');
const session = require('express-session');
const redisStore = require('connect-redis')(session);

let redisClient = redis.createClient(6379, 'redis');
let rabbitPublisher;
let clientsLogged = new Map();
let userlist = new Array();
let grantedUser = {id:"turnoff", username:"turnoff"};
let frontageConnected = false;


/*
 * Set up the server configuration :
 *   - distribute the static client
 *   - set the session config and expiration time (12h)
 */
function initServer() {

  // Init the session system
  let session = require('express-session')({
    secret: 'my-secret',
    resave: true,
    saveUninitialized: true,
    store: new redisStore({ host: 'localhost',
                            port: 6379,
                            client: redisClient,
                            ttl :  43200000 // time-to-live is set at 12 hours
                          }),
    cookie: {maxAge: 43200000} // time-to-live is set at 12 hours
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
      client.decotime = 0;
      client.status = "connected";
      clientsLogged.set(socket.handshake.session.id, client);
      let user = {id: client.id, username: client.login};
      userlist.push(user);
      // post userlist on redis
      console.log(userlist);
      redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
      if(client == grantedUser){
        socket.emit('granted');
      }
    }

    // When the user logs in (enter his/her name)
    socket.on('login', function (login) {
      if (!clientsLogged.has(socket.handshake.session.id)) {
        let time = (new Date()).getTime();
        clientsLogged.set(socket.handshake.session.id, {
          socket: socket,
          id: socket.handshake.session.id,
          firstlog: time,
          lastbeacon : time,
          login: login,
          decotime: 0,
          status: "connected",
          ip: socket.handshake.address
        });
        userlist.push({id: socket.handshake.session.id, username: login});
        // post userlist on redis
        console.log("user : "+ login + " has logged");
        console.log(userlist);
        redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
        let client = clientsLogged.get(socket.handshake.session.id);
        socket.emit('logged', {name: client.login, ip: client.ip});
      }
    });

    // When the user is disconnected he is marked it and removed from
    // the userlist
    socket.on('disconnect', function() {
      if (clientsLogged.has(socket.handshake.session.id)) {
        let client = clientsLogged.get(socket.handshake.session.id);
        client.status = "disconnected";
        clientsLogged.set(socket.handshake.session.id, client);
        let nuserlist = new Array();
        for (var user of userlist){
          if (user.id != client.id){
            nuserlist.push(user);
          }
        }
        if (client.id == grantedUser.id){
          grantedUser = {id: "turnoff", username: "turnoff"};
          redisClient.set('KEY_GRANTED_USER', JSON.stringify({id: "turnoff", username: "turnoff"}));
        }
        userlist = nuserlist;
        //post userlist on redis
        console.log(userlist);
        redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
      }
    });

    // Relay the update pixels to the live.py f-app
    socket.on('updateGrid',function(pixelsToUpdate){
      if (grantedUser.id === socket.handshake.session.id){
        //post pixelsToUpdate on RabbitMQ
        let msg = JSON.stringify({pixels: pixelsToUpdate});
        rabbitPublisher.publish('logs', '', Buffer.from(msg));
      }
    });

    // Beacon handler
    socket.on('isAlive', function(){
      let client = clientsLogged.get(socket.handshake.session.id);
      client.lastbeacon = (new Date()).getTime();
    });
  });
}

/**
 * grant a user designated by the admin user of mobile app
 * @param {Object} user format has to be {id : string, username: string}
 */
function grant(user) {
  if (user['id'] != "turnoff") {
    console.log(user.username + " has been granted");
    if (clientsLogged.get(user['id']) == null ){
      redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
      redisClient.set('KEY_GRANTED_USER', JSON.stringify({id: "turnoff", username: "turnoff"}));
    } else {
      clientsLogged.get(user['id']).socket.emit('granted');
    }
  }
}

/**
 * ungrant a user
 * @param {Object} user format has to be {id : string, username: string}
 */
function ungrant(user){
  if (user['id'] != "turnoff") {
    console.log(user.username +" has been ungranted");
    if (clientsLogged.get(user['id']) == null ){
      redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
      redisClient.set('KEY_GRANTED_USER', JSON.stringify({id: "turnoff", username: "turnoff"}));
    } else {
      clientsLogged.get(user['id']).socket.emit('ungranted');
    }
  }
}

/**
 * set /public/config.json to match with the configuration set up at frontage installation
 * @param {Object} data is retrived from redis
 */
async function updateConfigFile(data) {
  let conf = {
    language: "fr",
    rows: data['rows'],
    cols: data['cols'],
    disabled: data['disabled'],
    project: "Frontage",
    simuation: false};
  fs.writeFile("./public/config.json", JSON.stringify(conf), function(err) {
    if (err) throw err;
  });
  console.log("config.json modified !");
}

/**
 * get informations about frontage geometry and the granted user.
 */
function updateValues(){
  redisClient.get('KEY_FRONTAGE_HAS_CHANGED', function(err, reply) {
    let change_config = JSON.parse(reply);
    if (change_config != null && change_config.haschanged){
      change_config.haschanged = false;
      redisClient.set('KEY_FRONTAGE_HAS_CHANGED', JSON.stringify(change_config));
      updateConfigFile(change_config);
    }
  });
  redisClient.get('KEY_GRANTED_USER', function(err, reply) {
    let newGranted = JSON.parse(reply);
    if (newGranted != null && newGranted['id'] != grantedUser['id']){
      ungrant(grantedUser);
      grant(newGranted);
      grantedUser = newGranted;
    }
  });
}

/**
 * update the decotime value of deconnected clients
 * kick session too old (time to be considered too old depends on status)
 */
function sessionManager() {
  let now = (new Date()).getTime();
  for (var session of clientsLogged.values()) {
    if (session.status == "disconnected"){
      session.decotime += 600000;
      console.log("session : " + session.login + " has been down for " + session.decotime + " ms");
    }
    if (session.decotime >= 21600000){
      clientsLogged.delete(session.id);
      console.log("session "+ session.login +" has been revoked");
    }
    if ((now - session.firstlog) >= 43200000){
      clientsLogged.delete(session.id);
      console.log("session "+ session.login +" has expired");
    }
  }
}

/**
 * check if a client is unexpectedly inaccessible (wifi lost)
 */
function sessionChecker(){
  let time = (new Date()).getTime();
  for (var client of clientsLogged.values()){
    try {
      if ((time - client.lastbeacon) > 3000){
        throw (new Error());
      } else {
        client.socket.emit('isAlive');
      }
    } catch (e) {
      client.status = "disconnected";
      clientsLogged.set(client.id, client);
      let nuserlist = new Array();
      for (var user of userlist){
        if (user.id != client.id){
          nuserlist.push(user);
        }
      }
      if (client.id == grantedUser.id){
        grantedUser = {id: "turnoff", username: "turnoff"};
        redisClient.set('KEY_GRANTED_USER', JSON.stringify({id: "turnoff", username: "turnoff"}));
      }
      userlist = nuserlist;
      //post userlist on redis
      console.log(userlist);
      redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));
    }
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
  console.log("pika connection started");
});

initServer();
initSocket();

redisClient.set('KEY_USERS', JSON.stringify({users: userlist}));

// update granted user and rabbitmq publisher state each 1000ms
setInterval(updateValues, 1000); // invoke every second
setInterval(sessionChecker, 1000); // invoke every second
setInterval(sessionManager, 60000); // invoke every minute
