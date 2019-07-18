/**
 * @fileoverview This file contains the application's core functions (client-side on browser)
 */
const socket = (simulation_enabled ? null : io());
let granted = false;
let isRunning = false;
let updateTimer;
let pixelsToUpdate = [];
let blocklyWorker;
let sharedBuffer;
let sharedArray;



// Functions


/**
 * Runs the blockly program and launch the grid autoupdate
 */
function run() {
    if (!isRunning) {
        updateTimer = setInterval(updateArbalet, 100);

        blocklyWorker = new Worker('/blocklyWorker.js');

        blocklyWorker.postMessage({
          message: 'gridLength',
          nbRows: nbRows,
          nbColumns: nbColumns
        });

        blocklyWorker.postMessage({
          message: 'scripts',
          scripts: generateScripts()
        });

        blocklyWorker.onmessage = function (event) {
          if (event.data.message == 'close') {
            stop();
          } else {
            if (event.data.log != ""){
              console.log(event.data.log);
            }
            updatePixel(event.data.rowX, event.data.columnY, event.data.color);
          }

        };
        // All data sent to the worker, it can run the program
        blocklyWorker.postMessage({
          message: "run"
        });
        isRunning = true;
        switchPlayStopColors();
    }
}

/**
 * Stops the blockly program and the grid autoupdate
 */
function stop() {
    if (isRunning) {
        updateArbalet();
        clearInterval(updateTimer);
        blocklyWorker.terminate();
        isRunning = false;
        switchPlayStopColors();
    }
}

/**
 * Save the current workspace on a downloadable file (.xml)
 * @param {String} name File name of the exported workspace
 */
function save(name) {
    let domWorkspace = Blockly.Xml.workspaceToDom(workspace);
    let textWorkSpace = Blockly.Xml.domToText(domWorkspace);
    let textParam = `<arbalet><param><nbRows>${nbRows}</nbRows><nbColumns>${nbColumns}</nbColumns><disabled>`
                    + pixmlify(disabled_pixels)
                    + `</disabled></param><version>${softVersion}</version><blockly>`;
    if (name != null) {
        download(textParam + textWorkSpace + `</blockly></arbalet>`, name + '.xml', "application/xml");
    }
}


function BuildXMLFromString(text) {
  var message = "";
  if (window.DOMParser) { // all browsers, except IE before version 9
    var parser = new DOMParser();
    try {
      xmlDoc = parser.parseFromString(text, "text/xml");
    } catch (e) {
      // if text is not well-formed,
      // it raises an exception in IE from version 9
      console.log("XML parsing error.");
      return false;
    };
  }
  else {  // Internet Explorer before version 9
    xmlDoc = CreateMSXMLDocumentObject();
    if (!xmlDoc) {
      console.log("Cannot create XMLDocument object");
      return false;
    }

    xmlDoc.loadXML(text);
  }

  var errorMsg = null;
  if (xmlDoc.parseError && xmlDoc.parseError.errorCode != 0) {
    errorMsg = "XML Parsing Error: " + xmlDoc.parseError.reason
    + " at line " + xmlDoc.parseError.line
    + " at position " + xmlDoc.parseError.linepos;
  }
  else {
    if (xmlDoc.documentElement) {
      if (xmlDoc.documentElement.nodeName == "parsererror") {
        errorMsg = xmlDoc.documentElement.childNodes[0].nodeValue;
      }
    }
    else {
      errorMsg = "XML Parsing Error!";
    }
  }

  if (errorMsg) {
    console.log(errorMsg);
    return false;
  }

  console.log("Parsing was successful!");
  return xmlDoc;
}

/**
 * Import and set the current workspace with a downloaded .xml file
 */
function importWorkspace() {
    let selectedFile = document.getElementById('fileImport').files[0];
    let reader = new FileReader();
    reader.onload = function (event) {
        try {
          let xmltext = BuildXMLFromString(reader.result);
          if (!xmltext){
            throw("error: not an xml");
          }
          let racine = xmltext.documentElement;
          if (racine.nodeName == "arbalet"){
            var blocklytext = racine.getElementsByTagName("blockly")[0].innerHTML;
            var docRows = racine.getElementsByTagName("nbRows")[0].innerHTML;
            var docColumns = racine.getElementsByTagName("nbColumns")[0].innerHTML;
            if (simulation_enabled){
              var pixels = pixmlparse(racine.getElementsByTagName("pixel"));
              setconfig(docRows, docColumns, pixels);
              createLedTable(docRows, docColumns);
            } else if (docRows != nbRows || docColumns != nbColumns){
              throw("error : the dimensions do not match");
            }
          }else {
            var blocklytext = racine.outerHTML;
          }
          let blocklyxml = Blockly.Xml.textToDom(blocklytext);
          Blockly.Xml.clearWorkspaceAndLoadFromXml(blocklyxml, workspace);
          stop();
        } catch (error) {
          console.log(error);
          alert(selectedFile.name + " n'est pas un fichier Arbalet valide");
        }
    };
    reader.readAsText(selectedFile);
}

/**
 * Try to load an example file in the workspace
 * @param {String} fileName the example file name
 */
function loadExemple(fileName){
    $.ajax({
        method: 'GET',
        url: `exemples/${fileName}`,
        processData: false
    }).done(data => {
        Blockly.Xml.clearWorkspaceAndLoadFromXml(data.firstChild,workspace);
        stop();
    });
}

/**
 * Update the material Arbalet pixel grid if granted
 */
function updateArbalet() {
    if (pixelsToUpdate.length != 0 && granted && !simulation_enabled) {
        socket.emit('updateGrid', pixelsToUpdate);
        pixelsToUpdate = [];
    }
}

/**
 * Update a pixel on simulation and add it to the update queue
 * @param {Number} rowX The row of the pixel to update
 * @param {Number} columnY The column of the pixel to update
 * @param {String} color The color to set to the pixel
 */
function updatePixel(rowX, columnY, color) {
    let cell = {
        rowX: rowX,
        columnY: columnY,
        color:color
    };
    let cssCell = 'div[data-r=' + rowX + '][data-c=' + columnY + ']';
    if (granted) {
        pixelsToUpdate.push(cell);
    }
    $(cssCell).css('background', color);
}

/**
 * Translate workspace's blocks in Javascript (main program and events code)
 * @return {Object} An associative array of the scripts (5 elements max)
 */
function generateScripts() {
    Blockly.JavaScript.init(workspace);
    let scripts = {};
    let functionsDefinition = generateFunctions();
    let noEventProgram = true;

    Blockly.mainWorkspace.getBlocksByType("event_key").forEach(function (bloc) {
        let key = bloc.inputList[0].fieldRow[1].value_;
        let code = Blockly.JavaScript.blockToCode(bloc);
        scripts[key] = functionsDefinition + code;
        noEventProgram = false;
    });
    let ind = 0;
    if (Blockly.mainWorkspace.getBlocksByType("main_script").length > 1){
      let mains = "";
      for (var submain of Blockly.mainWorkspace.getBlocksByType("main_script")){
        mains += `async function main${ind}(){\n await sleep(10, 'ms');` +
                        functionsDefinition + Blockly.JavaScript.blockToCode(submain) +
                        `}\n `;
        ind += 1;
      }
      let mainm = "await Promise.all([";
      for (let j = 0; j < ind-1 ; j++){
        mainm += `main${j}(),`;
      }
      mainm += `main${ind-1}()`;
      scripts["main"] = mains + mainm + "]);";
    } else {
      scripts["main"] = "async function main(){" +
                      functionsDefinition +
                      Blockly.JavaScript.blockToCode(Blockly.mainWorkspace.getBlocksByType("main_script")[0]) +
                      "} await main();";
    }
    if(noEventProgram ){
      scripts["main"] += 'self.postMessage({message: "close"});close();' ;
    }
    return scripts;
}

/**
 * Translate functions' blocks in JavaScript code
 * @return {String} JavaScript code corresponding to the blockly functions defined in the workspace
 */
function generateFunctions() {
    Blockly.JavaScript.init(workspace);
    let functionsCode = '';

    let functionsBlocs = Blockly.mainWorkspace.getBlocksByType("procedures_defreturn");
    functionsBlocs.push(...Blockly.mainWorkspace.getBlocksByType("procedures_defnoreturn"));

    functionsBlocs.forEach((bloc) => {
        bloc.comment = '';
        Blockly.JavaScript.blockToCode(bloc);
    });

    // Variables declarations are deleted, so they will be global and shared between the main script and event scripts
    if (Blockly.mainWorkspace.getBlocksByType("event_key").length > 0){
      delete Blockly.JavaScript.definitions_.variables;
    }

    let arrayFunctions = Object.values(Blockly.JavaScript.definitions_);
    arrayFunctions = arrayFunctions.map((x) => {
        if(x != '' && x.substr(0,3) != 'var'){
            return 'async ' + x;
        } else if (x.substr(0,3) == 'var'){
          return x;
        }
    });

    functionsCode = arrayFunctions.join('');
    return functionsCode;
}
