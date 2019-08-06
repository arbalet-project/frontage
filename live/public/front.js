/**
 * @fileoverview This file contains all the graphical functions and event manager that work with the interface (client-side on browser)
 * @see mainClient.js
 */
let name = "";
document.getElementById('user-name-input').value = generateNickname();
document.getElementById('version').innerHTML += softVersion;
let workspace;
let lastbeacon = null;

createLedTable(nbRows, nbColumns, disabled_pixels);
initWorkspace();

if(!simulation_enabled){
  socket.on('logged',(user) => {
      $('#user-name').text(user.name);
      $('#user-ip').text(user.ip);
      //hideLoginScreen();
      lastbeacon = (new Date()).getTime();
      $('.overlay-popup').hide();
  });

  socket.on('granted', function () {
      granted = true;
      $('.connect-style').replaceWith('<p class="connect-style live">live</p>');
  });

  socket.on('ungranted', function () {
      granted = false;
      $('.live').replaceWith('<p class="connect-style">Connecté</p>');
  });

  socket.on('isAlive', function () {
    lastbeacon = (new Date()).getTime();
    socket.emit('isAlive');
    console.log("isAlive replied");
  });

  function beaconChecker() {
    console.log("beanconChecker");
    if ( (lastbeacon != null) && (new Date()).getTime() - lastbeacon > 3000){
      granted = false;
      $('.connect-style').replaceWith('<p class="connect-style">Déconnecté</p>');
    }
  }

  setInterval(beaconChecker, 1000);
} else {
  $('.info-user').css({
      "display": 'none'
  });
}
// Event keys for Blockly, stores the corresponding event in a sharedArray to be read by the worker
    $(document).on('keydown', function (e) {
        if (isRunning) {
            switch (e.which) {
                case 38: // UP
                    blocklyWorker.postMessage({message:'keyEvent', key: 'up'});
                    break;
                case 39: // RIGHT
                    blocklyWorker.postMessage({message:'keyEvent', key: 'right'});
                    break;
                case 40: // DOWN
                    blocklyWorker.postMessage({message:'keyEvent', key: 'down'});
                    break;
                case 37: // LEFT
                    blocklyWorker.postMessage({message:'keyEvent', key: 'left'});
                    break;
                case 32: // SPACE
                    blocklyWorker.postMessage({message:'keyEvent', key: 'space'});
                    break;
            }
        }
    });



// Animations and clicking behaviour definitions
$('#play').on('click', function (e) {
    e.preventDefault();
    run();
});

$('#stop').on('click', function (e) {
    e.preventDefault();
    stop();
});

$('#config').on('click', function (e) {
  e.preventDefault();
  settingForm();
  $('.overlay-popup3').fadeIn(200);
  $("#setting-module").fadeIn(200, function () {
    $('#setting-submit').on('click', function () {
      if (simulation_enabled){
        if (setconfig($('#setting-rows').val(), $('#setting-cols').val(), $('#setting-disabled').val())){
          createLedTable(nbRows, nbColumns);
          $('#setting-module').fadeOut(200);
          $('.overlay-popup3').fadeOut(200);
        } else {
          alert("invalid arguments");
        }
      } else{
        $('#setting-module').fadeOut(200);
        $('.overlay-popup3').fadeOut(200);
      }
    })
  })
})

$('#import').on('click', function (e) {
    e.preventDefault();
    if (Blockly.mainWorkspace.getAllBlocks().length > 1){
      if (!confirm('Êtes vous sûr(e) de vouloir continuer ?')){
        return;
      }
    }
    $('#fileImport').click();
    _paq.push(['trackEvent', 'Simulation', 'Load']);
});

$('#export').on('click', function () {
    document.getElementById('export-input').value = name.replace(' ', '_');
    $('.overlay-popup3').fadeIn(200);
    $("#export-module").fadeIn(200, function () {
        $('#export-file').on('click', function () {
            let name = $('#export-input').val();
            save(name);
            $('#export-module').fadeOut(200);
            $('.overlay-popup3').fadeOut(200);
        })
    })
})

$('#export-input').keypress(function (event) {
    if (event.which == 13) {
        $('#export-file').click();
        _paq.push(['trackEvent', 'Simulation', 'Save']);
    }
});

$('#fileImport').on('change', function (e) {
    importWorkspace();
});

$('#example').on('click', function () {
    $('.overlay-popup3').fadeIn(200);
    $('#example-module').fadeIn(200);
});

$('#file').on('click',function(){
  if (Blockly.mainWorkspace.getAllBlocks().length > 1){
    if (!confirm('Êtes vous sûr(e) de vouloir continuer ?')){
      return;
    }
  }
  _paq.push(['trackEvent', 'Simulation', 'New Workspace']);
  workspace.clear();
  let mainBlock = workspace.newBlock('main_script');
  mainBlock.initSvg();
  mainBlock.render();
  mainBlock.moveBy(300,30);
});

$('#challenges').on('click', function () {
    $('.overlay-popup3').fadeIn(200)
    $('#challenges-module').fadeIn(200)
})

$('#informations').on('click', function () {
    $('.overlay-popup3').fadeIn(200)
    $('#informations-module').fadeIn(200)
})

$('.overlay-popup3').on('click', function () {
    $(this).fadeOut(200, function () {
        $('#example-module').fadeOut(200)
        $('#export-module').fadeOut(200)
        $('#setting-module').fadeOut(200)
        $('#informations-module').fadeOut(200)
        $('#challenges-module').fadeOut(200)
    })
});

$('#full-screen').on('click', function (e) {
    e.preventDefault();
    toogleFullScreen();
});

$('.setting-menu').hover(function () {
    $('.info-user').fadeOut(200);
}, function () {
  if (!simulation_enabled){
    $('.info-user').fadeIn(200);
  }
});

$('#send-name').on('click', function () {
    name = $('#user-name-input').val()
    if(name != ""){
        hideLoginScreen();
        if (! simulation_enabled){
        socket.emit('login', name);
      }
    }
});

$('#user-name-input').keypress(function (event) {
    if (event.which == 13) {
        $('#send-name').click();
    }
});

$('#turn-led').on('click', function(e){
    e.preventDefault();
    $('#led-table').toggleClass('active-rotate');
    $(this).toggleClass('active-rotate-button');
});

$(".example-item").on('click',function(){
    loadExemple($(this).data('name'));
    $("#example-module").fadeOut(200);
    $('.overlay-popup3').fadeOut(200);
});

function hideLoginScreen(){
    $('.overlay-popup').css({
        "transition": "0.4s ease",
        "transform": " scale(1.05)"
    }).delay(500).fadeOut(400);
}

/**
 * Init the blockly workspace and the toolbox
 */
function initWorkspace() {
    let toolbox = document.getElementById('toolbox');

    // Creating the workspace
    workspace = Blockly.inject('blocklyDiv', {
        toolbox: toolbox,
        collapse: true,
        comments: true,
        disable: true,
        maxBlocks: Infinity,
        trashcan: true,
        horizontalLayout: false,
        toolboxPosition: 'start',
        css: true,
        rtl: false,
        scrollbars: false,
        sounds: true,
        oneBasedIndex: true
    });

    // Adding a program block to this workspace
    let mainBlock = workspace.newBlock('main_script');
    mainBlock.initSvg();
    mainBlock.render();
    mainBlock.moveBy(300,30);


}

/**
 * Tells if the i,j pixel is disabled
 * @param {Number} row
 * @param {Number} column
 */
function is_disabled(i,j){
  for (let pos of disabled_pixels) {
    if ((pos[0] == i) && (pos[1] == j)){
      return true;
    }
  }
  return false;
}

/**
 * Generate the HTML table of the pixels for the simulation
 * @param {Number} nbRows
 * @param {Number} nbColumns
 */
function createLedTable(nbRows, nbColumns) {
    let ledContainer = document.getElementById('led-table');
    ledContainer.innerHTML = "";
    for (let i = 0; i < nbRows; i++) {
        let newRow = ledContainer.insertRow();
        for (let j = 0; j < nbColumns; j++) {
          if (is_disabled(i, j)) {
            newRow.insertCell(j).innerHTML = `<div class="dled" data-r="${i}" data-c="${j}"></div>`;
          } else {
            newRow.insertCell(j).innerHTML = `<div class="led" data-r="${i}" data-c="${j}"><span>[${i},${j}]</span></div>`;
          }
        }
    }
}

/**
 * Toogle the full-screen mode of the simulation
 */
function toogleFullScreen() {
    if (!$('.led-content').hasClass('full-screen')) {
        $('.led-content').wrap('<div class="overlay-popup2"></div>');
        $('.led-content').addClass('full-screen');
    } else {
        $('.led-content').removeClass('full-screen');
        $('.overlay-popup2').contents().unwrap();
    }
}

/**
 * Switch the colors of Play and Stop buttons
 */
function switchPlayStopColors() {
    if (isRunning) {
        $('#play').css({
            "background-image": 'url(../asset/images/icon/play.png)'
        });
        $('#stop').css({
            "background-image": 'url(../asset/images/icon/stop_red.png)'
        });
    } else {
        $('#play').css({
            "background-image": 'url(../asset/images/icon/play_green.png)'
        });
        $('#stop').css({
            "background-image": 'url(../asset/images/icon/stop.png)'
        });
    }
}
