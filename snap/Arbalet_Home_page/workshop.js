

Blockly.JavaScript['text_length'] = function(block) {
    // String or array length.
    var argument0 = Blockly.JavaScript.valueToCode(block, 'VALUE',
        Blockly.JavaScript.ORDER_FUNCTION_CALL) || '\'\'';
    return [argument0 + '.length', Blockly.JavaScript.ORDER_MEMBER];
};