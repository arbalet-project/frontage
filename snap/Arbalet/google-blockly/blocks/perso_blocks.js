// eteindre tout: block definition:
Blockly.Blocks['perso_eteindre_tout'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Eteindre tout");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

// colorer un pixel : block definition:
Blockly.Blocks['perso_colorer_le_pixel'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Colorer le pixel")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j")
            .appendField("en :")
            .appendField(new Blockly.FieldColour("#ff0000"), "pixel");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(240);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

//colorer un pixel with input : block definition:
Blockly.Blocks['perso_colorer_pixel_alea'] = {
    init: function() {
        this.appendValueInput("NAME")
            .setCheck(null)
            .appendField("Colorer le pixel ")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j")
            .appendField("en");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

// eteindre un pixel : block definition
Blockly.Blocks['perso_eteindre_pixel'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Eteindre le pixel")
            .appendField(new Blockly.FieldNumber(0, 0, 3), "i")
            .appendField(new Blockly.FieldNumber(0, 0, 18), "j");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};


//eteindre tout: Generating into JS code :
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
        '            document.getElementById(i + \'-\' + j).style.fill = \'#FFFFFF\';\n' +
        '        }\n' +
        '    }}\n' +
        'ColorerToutEnNoir();';
    return code;
};

// colorer un pixel : Generatig its code JS:
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

// eteindre un pixel : Generating into Js code:
Blockly.JavaScript['perso_eteindre_pixel'] = function(block) {
    var number_i = block.getFieldValue('i');
    var number_j = block.getFieldValue('j');
    // TODO: Assemble JavaScript into code variable.
    var code = 'function eteindreLePixel(_i, _j) {\n' +
        '    document.getElementById(_i + "-" + _j).style.fill=\'#FFFFFF\';\n' +
        '}\n' +
        'eteindreLePixel('+ number_i + ',' + number_j + ');\n';
    return code;
};

//colorer un pixel with input : Generating code :
Blockly.JavaScript['perso_colorer_pixel_alea'] = function(block) {
    var number_i = block.getFieldValue('i');
    var number_j = block.getFieldValue('j');
    var value_name = Blockly.JavaScript.valueToCode(block, 'NAME', Blockly.JavaScript.ORDER_ATOMIC);
    // TODO: Assemble JavaScript into code variable.
    var code =  'function colorerLePixel_ij(_i, _j){\n' +
        '    document.getElementById( _i + "-" + _j).style.fill=' + '\'' +  + '\';\n' +
        '}\n' +
        'colorerLePixel_ij(' + number_i + ',' + number_j + ');\n';
    return code;
};