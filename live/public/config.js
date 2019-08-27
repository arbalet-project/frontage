/**
 * @fileoverview This file contains the setting application's handler
 */
 const softVersion = "1.1.1";

let config= {};
getconfig();

let nbRows = config["rows"];
let nbColumns = config["cols"];
let project = config["project"];
let language = config["language"];
let simulation_enabled = config["simulation"];
let disabled_pixels = config["disabled"];
configName();


// URL handler for number of rows and columns
params = new URLSearchParams(window.location.search)
if (params.has('rows')) {
    nbRows = parseInt(params.get('rows'));
}
if (params.has('cols')) {
    nbColumns = parseInt(params.get('cols'));
}


// Functions

/**
 * Get settings from the json file config.file and stock it in config variable.
 */
function getconfig() {
  $.ajax({
      method: 'GET',
      url: `/config.json`,
      processData: true,
      async : false
  }).done(data => {
    config = data;
  });
}

/**
 * Determine if pixelsarray is a string describing a right-format array
 * @param {String} pixelsarray a string
 * @param {Number} nr number of rows
 * @param {Number} nc number of columns
 */
function valid(pixelsarray, nr, nc){
  try {
    let array = JSON.parse(pixelsarray);
    for (var tmp of array){
      if (tmp[0] < 0 || tmp[0] >= nr || tmp[1] < 0 || tmp[1] >= nc){
        return false;
      }
    }
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Set config variables
 * @param {Number} nr number of rows
 * @param {Number} nc number of columns
 * @param {String} dpixels a string containing an array of the disabled pixels present in the matrix
 */
function setconfig(nr, nc, dpixels){
  if (nr <= 0 || nc <= 0 || !valid(dpixels, nr, nc)) {
    return false;
  }
  nbRows = nr;
  nbColumns = nc;
  disabled_pixels = JSON.parse(dpixels);
  return true;
}

function pixmlify(pixels){
  let xmlstring = "";
  for (var pix of pixels){
    xmlstring += `<pixel row="${pix[0]}" col="${pix[1]}"></pixel>`;
  }
  return xmlstring;
}

function pixmlparse(pixml){
  let pixels = [];
  for (var i = 0; i < pixml.length; i++){
    var pix = pixml[i];
    var atts = pix.attributes;
    pixels[i] = [parseInt(atts[0].value), parseInt(atts[1].value)];
  }
  return pixels;
}

/**
 * Set the app name in all its occurences
 */
function configName(){
  document.getElementById('doc-infoTitle').innerHTML = `Arbalet ${project} Live`;
  document.getElementById('doc-title').innerHTML = `Arbalet ${project} Live`;
  document.getElementById('doc-h1').innerHTML = `Arbalet ${project} Live`;
  document.getElementById('doc-startMod').innerHTML = `Bienvenue sur Arbalet ${project} Live !`;
  document.getElementById('doc-infoMod').innerHTML = `Arbalet ${project} Live est un projet opensource développé par les membres d'Arbalet Living Lab pour le <a href="http://www.arbalet-project.org">projet Arbalet</a>`
}

/**
 * Build the setting formular by displaying the current value in the form fields
 */
function settingForm() {
  if (!simulation_enabled){
    var disabled = `disabled`;
  } else {
    var disabled = ``;
  }
  document.getElementById('input-rows').innerHTML = `<input type="number" id="setting-rows" min="1" max="20" value=${nbRows} ` + disabled + ` />`;
  document.getElementById('input-cols').innerHTML = `<input type="number" id="setting-cols" min="1" max="20" value=${nbColumns} ` + disabled + ` />`;
  let msg = JSON.stringify(disabled_pixels);
  document.getElementById('input-disabled').innerHTML = `<input type="text" id="setting-disabled" value="${msg}" ` + disabled + ` />`;
}
