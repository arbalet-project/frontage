### NOTES :
##### Workshop.html :
This file contains three major parts: 
1. The call of all the blocks needed in an XML tag: 
* Once the blocks are defined in **perso_blocks.js** you have to call theme by adding the right name of the *block* to the right *category* already defined for example: <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`<category name="Text" colour="100">`<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`<block type="text_print"></block>` <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`</category>`
    
* To remove a block from the category all you have to do is removing the tag concerned. Same goes with categories.

2. SVG tag contains the screen image in svg format 
Each path is identified, we’ll need this IDs to access to paths through JS DOM to full the pixel.   

3 a mandatory script at the bottom of the page that generate the blocks code into JS code and copying it onto the text area,
  see : [Blockly official Documentaition Workspace](https://developers.google.com/blockly/guides/configure/web/resizable)

##### Scripts included are mainly from Blockly Library 
 *see documentation*  : [Blockly official Documentation ](https://developers.google.com/blockly/guides/get-started/web).
 
Another included Script is : *“\google-blockly\blocks\perso_blocks.js”* this file contains the definition of **custom blocks** and theirs codes generated into JavaScript.

In **Workshop.js** there are defined all the functions needed to color the pixels these functions use DOM to access to the SVG screen. 
