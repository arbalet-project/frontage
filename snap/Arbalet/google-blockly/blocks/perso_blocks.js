// turn off all: block definition:
Blockly.Blocks['perso_eteindre_tout'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Eteindre tout");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(75);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

// color a pixel : block definition:
Blockly.Blocks['perso_colorer_le_pixel'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Allumer le pixel")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j")
            .appendField("en :")
            .appendField(new Blockly.FieldColour("#ff0000"), "pixel");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(75);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

//color a pixel randomly : block definition:
Blockly.Blocks['perso_colorer_pixel_alea'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Allumer le pixel ")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j")
            .appendField("Aléatoirement");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(75);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

// random pixel randomly : Block definition
Blockly.Blocks['perso_pixel_x_alea'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Allumer n'importe quel pixel aléatoirement");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(75);
        this.setTooltip("Attention, ne pas abuser d'utilisation !");
        this.setHelpUrl();
    }
};

// turn off a pixel : block definition
Blockly.Blocks['perso_eteindre_pixel'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Eteindre le pixel")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(75);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

//END OF DEFIINITIONS // ******************************


//turn off all: Generating into JS code :
Blockly.JavaScript['perso_eteindre_tout'] = function(block) {
    // TODO: Assemble JavaScript into code variable.
    var code = 'function ColorerToutEnNoir() {\n' +
        '    var i_tab = new Array(4);\n' +
        '    var j_tab = new Array(19);\n' +
        '    for (var i = 0; i < i_tab.length; i++) {\n' +
        '        for (var j = 0; j < j_tab.length; j++) {\n' +
        '            if ( i === 3) {\n' +
        '                if (j === 7){\n' +
        '                    j=j+4;\n' +
        '                    continue;\n' +
        '                }\n' +
        '            }\n' +
        '            document.getElementById(i + \'-\' + j).style.fill = \'#000000\';\n' +
        '        }\n' +
        '    }}\n' +
        'ColorerToutEnNoir();';
    return code;
};

// color a pixel  : Generatig its code JS:
Blockly.JavaScript['perso_colorer_le_pixel'] = function(block) {
    var number_i = block.getFieldValue('i');
    var number_j = block.getFieldValue('j');
    var colour_pixel = block.getFieldValue('pixel');
    // TODO: Assemble JavaScript into code variable.
    var code = 'function colorerLePixel_ij(_i, _j, _color){\n' +
        '    document.getElementById( _i + "-" + _j).style.fill=_color;\n' +
        '}\n' +
        'colorerLePixel_ij(' + number_i + ',' + number_j + ',' + '\'' + colour_pixel + '\'' + ');\n';
    return code;
};

//color the pixel (ij) randomly : Generating code :
Blockly.JavaScript['perso_colorer_pixel_alea'] = function(block) {
    var number_i = block.getFieldValue('i');
    var number_j = block.getFieldValue('j');
    // TODO: Assemble JavaScript into code variable.
    var code = 'function Colorer_le_pixel_alea(_i, _j){\n' +
        '    document.getElementById(_i + "-" + _j).style.fill=RandomColor();\n' +
        '}\n' +
        'Colorer_le_pixel_alea('+ number_i+',' + number_j+')\n';
    return code;
};

// random pixel randomly Generating code :
Blockly.JavaScript['perso_pixel_x_alea'] = function(block) {
    // TODO: Assemble JavaScript into code variable.
    var code = 'function Color_pixel_X_alea(){\n' +
        '    document.getElementById( Math.floor(Math.random() * Math.floor(4)) + "-" + Math.floor(Math.random() * Math.floor(19)) ).style.fill=RandomColor();\n' +
        '}\n' +
        'Color_pixel_X_alea();\n';
    return code;
};

// turn off a pixel : Generating into Js code:
Blockly.JavaScript['perso_eteindre_pixel'] = function(block) {
    var number_i = block.getFieldValue('i');
    var number_j = block.getFieldValue('j');
    // TODO: Assemble JavaScript into code variable.
    var code = 'function eteindreLePixel(_i, _j) {\n' +
        '    document.getElementById(_i + "-" + _j).style.fill=\'#000000\';\n' +
        '}\n' +
        'eteindreLePixel('+ number_i + ',' + number_j + ');\n';
    return code;
};
