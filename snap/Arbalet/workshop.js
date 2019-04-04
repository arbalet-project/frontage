
//turn all pixels off:
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

//Color the pixel (i,j)
function colorerLePixel_ij(_i, _j, _color){
    document.getElementById(_i + "-" + _j).style.fill=_color;
}

//turn off the pixel(i,j)
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

//Color randomly :
function Colorer_le_pixel_alea(_i, _j){
    document.getElementById(_i + "-" + _j).style.fill=RandomColor();
}

//RandomColor Function:
/**
 * @return {string}
 */
function RandomColor() {
    let r = Math.floor(Math.random() * Math.floor(256));
    let g = Math.floor(Math.random() * Math.floor(256));
    let b = Math.floor(Math.random() * Math.floor(256));
    console.log(r,g,b)
    return `rgb(${r},${g},${b})`;
}

//color random pixel randomly:
function Color_pixel_X_alea(){
    document.getElementById( Math.floor(Math.random() * Math.floor(4)) + "-" + Math.floor(Math.random() * Math.floor(19)) ).style.fill=RandomColor();
}
