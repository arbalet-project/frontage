// Management of the received messages on websockets

socket.on('logged',(user) => {
    $('#user-name').text(user.name);
    $('#user-ip').text(user.ip);
    //hideLoginScreen();
    $('.overlay-popup').hide();
});

socket.on('granted', function () {
    granted = true;
    $('.connect-style').replaceWith('<p class="connect-style live">live</p>');
});

socket.on('ungranted', function () {
    granted = false;
    $('.live').replaceWith('<p class="connect-style">Connecté au poste</p>');
});
