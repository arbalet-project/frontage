//tout eteindre:
function ColorerToutEnNoir() {
    var i_tab = new Array(4);
    var j_tab = new Array(19);
    for (var i = 0; i < i_tab.length; i++) {
        for (var j = 0; j < j_tab.length; j++) {
            if ( i === 3) {
                if (j === 7){
                    j=j+4;
                    continue;
                }
            }
            document.getElementById(i + '-' + j).style.fill = '#000000';
        }
    }
}

//colorer le pixel (i,j)
function colorerLePixel_ij(_i, _j, _color){
    document.getElementById(_i + "-" + _j).style.fill=_color;
}
colorerLePixel_ij(_i,_j,_color);

//eteindre le pixel(i,j)
function eteindreLePixel(_i, _j) {
    document.getElementById(_i + "-" + _j).style.fill='#FFFFFF';
}

//show code JS :
function showCode() {
    var x = document.getElementById("textarea");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}
function isShown() {
    var x = document.getElementById("textarea");
    if (x.style.display = "block")
        return true;
    else return false;
}

//run code JS :
function runCode() {
    window.LoopTrap = 1000;
    Blockly.JavaScript.INFINITE_LOOP_TRAP = 'if(--window.LoopTrap == 0) throw "Infinite loop.";\n';
    var codeJS = Blockly.JavaScript.workspaceToCode(workspace);
    try {
        eval(codeJS);
    } catch (e) {
        alert(e);
    }
};

//stopcode :
function clearCode() {
    document.getElementById('textarea').value ='';
workspace.addChangeListener(myUpdateFunction);}