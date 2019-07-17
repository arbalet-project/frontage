/**
 * @fileoverview This file is the script loaded by the worker that runs the blockly generated code
 */

importScripts('charMap.js');

let nbrows;
let nbcolumns;
let gridState = [];

let scripts;

/**
 * Event listener for message reception, it handles 4 types of message:
 * - gridLength setting the number of rows and columns
 * - scripts reveiving the different code to execute (5 max: 1 main script and 4 event scripts)
 * - run executing the main script, the worker can't handle more messages after receiving this one
 */
onmessage = function (e) {
    switch (e.data.message) {
        case 'gridLength':
            nbrows = e.data.nbRows;
            nbcolumns = e.data.nbColumns;
            for (let i = 0; i < nbrows; i++) {
                gridState[i] = [];
            }
            break;

        case 'keyEvent':
            run(scripts[e.data.key]);
            break;

        case 'scripts':
            scripts = e.data.scripts;
            break;

        case 'run':
            run(scripts['main']);
            break;

        default:
            break;
    }
}

/**
 * Set a specified pixel to the chosen color by sending a message to the main thread
 * @param {Object} pixel The pixel is a pixel object {'r':number, 'c':number}
 * @param {String} color The color to set to the pixel
 */
function setPixel(pixel, color) {
  var rowX = pixel['r'];
  var columnY = pixel['c'];
    if ((rowX >= 0 && rowX < nbrows) && (columnY >= 0 && columnY < nbcolumns)) {
        self.postMessage({
            rowX: rowX,
            columnY: columnY,
            color: color,
            log :""
        });
        gridState[rowX][columnY] = color;
    } else {
      self.postMessage({
          rowX: rowX,
          columnY: columnY,
          color: color,
          log :"nok"
      });
    }
}

/**
 * Set a specified pixel to the chosen color by sending a message to the main thread
 * @param {Object} pixel The pixel is a pixel object {'r':number, 'c':number}
 * @param {String} direction The direction in which the next pixel is in the pixel perspective
 */
function nextPixel(pixel, direction) {
  var npixel = {'r': pixel['r'], 'c':pixel['c']};
  switch (direction) {
    case 'UP':
      npixel['r'] = pixel['r'] -1;
      break;
    case 'DOWN':
      npixel['r'] = pixel['r'] +1;
      break;
    case 'RIGHT':
      npixel['c'] = pixel['c'] +1;
      break;
    case 'LEFT':
      npixel['c'] = pixel['c'] -1;
      break;
    default:
  }
  if (npixel['r'] < 0){
    npixel['r'] = nbrows -1;
  } else if (npixel['r'] >= nbrows){
    npixel['r'] = 0;
  }
  if (npixel['c'] < 0){
    npixel['c'] = nbcolumns -1;
  } else if (npixel['c'] >= nbcolumns){
    npixel['c'] = 0;
  }
  return npixel;
}

/**
 * Tell if the item is in the list, item can be an object
 * @param {Object} item a object, can be primitive or not
 * @param {List} list an object list
 */
function isInList(item, list){
  var search = JSON.stringify(item);
  for (var candidat of list){
    if (JSON.stringify(candidat) == search){
      return true;
    }
  }
  return false;
}


/**
 * Set the specified pixel off (set the pixel color to black)
 * @param {Number} rowX The pixel's row in the grid
 * @param {Number} columnY The pixel's column in the grid
 */
function switchOffPixel(pixel) {
    setPixel(pixel, '#000000');
}

/**
 * Set all pixels off
 */
function switchOffAllPixels() {
    for (let i = 0; i < nbrows; i++) {
        for (let j = 0; j < nbcolumns; j++) {
            switchOffPixel({'r':i,'c':j});
        }
    }
}

/**
 * Set all pixels to the given color
 * @param {String} color The color to set to the pixel
 */
function setAllPixels(color) {
    for (let i = 0; i < nbrows; i++) {
        for (let j = 0; j < nbcolumns; j++) {
          let pixel = {'r':i, 'c':j};
            setPixel(pixel, color);
        }
    }
}

/**
 * Return the current color of the specified pixel
 * @param {Number} row
 * @param {Number} column
 * @returns {String}
 */
function getPixelColor(pixel) {
  var row = pixel['r'];
  var column = pixel['c'];
    if(row < 0 || column < 0 || row >= nbrows || column >= nbcolumns){
        return '#000000';
    }
    else{
        return gridState[row][column];
    }

}

/**
 * Draw the specified letter to the given position and with the given direction
 * @param {String} inputLetter The letter to draw (only the first character of the string)
 * @param {Number} rowX The row number of the left-top pixel of the letter
 * @param {Number} columnY The column number of the left-top pixel of the letter
 * @param {String} color The color of the letter
 * @param {Number} direction The direction the letter has to be drawn (0 = vertical, 1 = horizontal)
 */
function drawLetter(inputLetter, rowX, columnY, color, direction) {
    let letter = inputLetter.charAt(0);
    if (charMap.has(letter)) {
        let letterPixels = charMap.get(letter);
        for (let i = 0; i < letterPixels.length; i = i + 2) {
          let pixel = {'r':0, 'c':0};
            if (direction == 0) {
              pixel['r'] = rowX + letterPixels[i];
              pixel['c'] = columnY + letterPixels[i + 1];
                setPixel(pixel, color);
            } else {
              pixel['r'] = rowX + letterPixels[i + 1];
              pixel['c'] = columnY - letterPixels[i];
                setPixel(pixel, color);
            }
        }

    }
}

/**
 * Sleep the program for the given time
 * @param {Number} time The quantity of time to sleep (in seconds or milliseconds)
 * @param {String} unit The unit of time to sleep (s or ms)
 */
function sleep(time, unit) {
    time = ((unit == 's') ? time*1000 : time);
    return new Promise(resolve => setTimeout(resolve, time));
  }

async function run(script){
    var AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
    let functionScript = new AsyncFunction(script);
    functionScript();
}

/**
 * Generate a random hexadecimal color
 * This function is natively in Blockly but needs to be redefined in that use
 * @returns {String}
 */
function colourRandom() {
    var num = Math.floor(Math.random() * Math.pow(2, 24));
    return '#' + ('00000' + num.toString(16)).substr(-6);
}

/**
 * Generate a color with the specified amount of red,green and blue
 * This function is natively in Blockly but needs to be redefined in that use
 * @param {Number} red The amount of red in the color
 * @param {Number} green The amount of green in the color
 * @param {Number} blue The amount of blue in the color
 * @returns {String}
 */
function colourRgb(red, green, blue) {
    red = Math.max(Math.min(Number(red), 100), 0) * 2.55;
    green = Math.max(Math.min(Number(green), 100), 0) * 2.55;
    blue = Math.max(Math.min(Number(blue), 100), 0) * 2.55;
    red = ('0' + (Math.round(red) || 0).toString(16)).slice(-2);
    green = ('0' + (Math.round(green) || 0).toString(16)).slice(-2);
    blue = ('0' + (Math.round(blue) || 0).toString(16)).slice(-2);
    return '#' + red + green + blue;
}

/**
 * Generate a color by blending two colors
 * This function is natively in Blockly but needs to be redefined in that use
 * @param {Number} c1 The first color to blend
 * @param {Number} c2 The second color to blend
 * @param {Number} ratio The ratio of "blending" of the two colors
 * @returns {String} The generated colour
 */
function colourBlend(c1, c2, ratio) {
    ratio = Math.max(Math.min(Number(ratio), 1), 0);
    var r1 = parseInt(c1.substring(1, 3), 16);
    var g1 = parseInt(c1.substring(3, 5), 16);
    var b1 = parseInt(c1.substring(5, 7), 16);
    var r2 = parseInt(c2.substring(1, 3), 16);
    var g2 = parseInt(c2.substring(3, 5), 16);
    var b2 = parseInt(c2.substring(5, 7), 16);
    var r = Math.round(r1 * (1 - ratio) + r2 * ratio);
    var g = Math.round(g1 * (1 - ratio) + g2 * ratio);
    var b = Math.round(b1 * (1 - ratio) + b2 * ratio);
    r = ('0' + (r || 0).toString(16)).slice(-2);
    g = ('0' + (g || 0).toString(16)).slice(-2);
    b = ('0' + (b || 0).toString(16)).slice(-2);
    return '#' + r + g + b;
}

/**
 * Generate a random integer between a and b
 * This function is natively in Blockly but needs to be redefined in that use
 * @param {Number} a
 * @param {Number} b
 * @returns {String} The generated number
 */
function mathRandomInt(a, b) {
    if (a > b) {
      // Swap a and b to ensure a is smaller.
      var c = a;
      a = b;
      b = c;
    }
    return Math.floor(Math.random() * (b - a + 1) + a);
  }

async function scrollingText(texte, numColonne, col, bg_col){
  let i = 0;
  var repeat_end = texte.length * 9;
  setAllPixels(bg_col);
  for (var count = 0; count < repeat_end; count++) {
    var i_end = texte.length;
    var i_inc = 1;
    if (0 > i_end) {
      i_inc = -i_inc;
    }
    for (i = 0; i_inc >= 0 ? i <= i_end : i >= i_end; i += i_inc) {
      drawLetter((texte.charAt((i - 1))),(numColonne + i * 7),8,col,1);
    }
    await sleep(200,'ms');var i_end2 = texte.length;
    var i_inc2 = 1;
    if (0 > i_end2) {
      i_inc2 = -i_inc2;
    }
    for (i = 0; i_inc2 >= 0 ? i <= i_end2 : i >= i_end2; i += i_inc2) {
      drawLetter((texte.charAt((i - 1))),(numColonne + i * 7),8,bg_col,1);
    }
    numColonne = numColonne - 1;
  }
}
