/**
 * @fileoverview This file define our custom blocks
 */

Blockly.defineBlocksWithJsonArray([{
    "type": "color_pixel",
    "message0": "%{BKY_COLOR_PIXEL_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "pixel",
      },
      {
        "type": "input_value",
        "name": "color",
        "align": "RIGHT"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "%{BKY_COLOR_PIXEL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "next_pixel",
    "message0": "%{BKY_NEXT_PIXEL_TITLE}",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "position",
        "options": [
          [
            "en haut",
            "'UP'"
          ],
          [
            "en bas",
            "'DOWN'"
          ],
          [
            "à droite",
            "'RIGHT'"
          ],
          [
            "à gauche",
            "'LEFT'"
          ]
        ]
      },
      {
        "type": "input_value",
        "name": "pixel"
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": 0,
    "tooltip": "%{BKY_NEXT_PIXEL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "pixel_item",
    "message0": "%{BKY_PIXEL_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "ROW",
        "check": "Number",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "COL",
        "check": "Number"
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": 0,
    "tooltip": "%{BKY_PIXEL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "color_all_pixels",
    "message0": "%{BKY_COLOR_ALL_PIXELS_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "color",
        "check": "Colour"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "%{BKY_COLOR_ALL_PIXELS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "turn_off_the_pixel",
    "message0": "%{BKY_TURN_OFF_THE_PIXEL_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "pixel",
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "%{BKY_TURN_OFF_THE_PIXEL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "turn_off",
    "message0": "%{BKY_TURN_OFF_TITLE}",
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "%{BKY_TURN_OFF_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "var_max_column",
    "message0": "%{BKY_VAR_MAX_COLUMN_TITLE}",
    "inputsInline": true,
    "output": "Number",
    "colour": 0,
    "tooltip": "%{BKY_VAR_MAX_COLUMN_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "var_max_line",
    "message0": "%{BKY_VAR_MAX_ROW_TITLE}",
    "output": "Number",
    "colour": 0,
    "tooltip": "%{BKY_VAR_MAX_ROW_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "pixel_color",
    "message0": "%{BKY_PIXEL_COLOR_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "pixel",
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": 20,
    "tooltip": "%{BKY_PIXEL_COLOR_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "sleep",
    "message0": "%{BKY_SLEEP_TITLE}",
    "args0": [
      {
        "type": "input_value",
        "name": "time"
      },
      {
        "type": "field_dropdown",
        "name": "list",
        "options": [
          [
            "s",
            "'s'"
          ],
          [
            "ms",
            "'ms'"
          ]
        ]
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 120,
    "tooltip": "%{BKY_SLEEP_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "scrolling_text",
    "message0": "%{BKY_SCROLL_TITLE}",
    "args0": [
      {
        "type": "field_input",
        "name": "text",
        "text": "ENSEIRB"
      },
      {
        "type": "input_value",
        "name": "col"
      },
      {
        "type": "input_value",
        "name": "color"
      },
      {
        "type": "input_value",
        "name": "bgcolor"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 165,
    "tooltip": "%{BKY_SCROLL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "draw_letter",
    "message0": "Dessiner la lettre %1 à %2 %3 en %4 %5",
    "args0": [
      {
        "type": "input_value",
        "name": "letter",
        "check": "String"
      },
      {
        "type": "input_value",
        "name": "row",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "column",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "color",
        "check": "Colour"
      },
      {
        "type": "field_dropdown",
        "name": "direction",
        "options": [
          [
            "↕",
            "0"
          ],
          [
            "↔",
            "1"
          ]
        ]
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 165,
    "tooltip": "Dessine la lettre écrite dans la couleur correspondante. Les coordonnées sont celles du coin en haut à gauche.",
    "helpUrl": ""
  },
  {
    "type": "event_key",
    "message0": "Touche %1 pressée %2 %3",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "key",
        "options": [
          [
            "↑",
            "up"
          ],
          [
            "→",
            "right"
          ],
          [
            "↓",
            "down"
          ],
          [
            "←",
            "left"
          ],
          [
            "espace",
            "space"
          ]
        ]
      },
      {
        "type": "input_dummy"
      },
      {
        "type": "input_statement",
        "name": "event_code"
      }
    ],
    "inputsInline": false,
    "colour": 270,
    "tooltip": "Le code contenu dans ce bloc s'exécute lorsque la touche correspondante est pressée.",
    "helpUrl": ""
  },
  {
    "type": "main_script",
    "message0": "Programme %1 %2",
    "args0": [
      {
        "type": "input_dummy"
      },
      {
        "type": "input_statement",
        "name": "script"
      }
    ],
    "colour": 270,
    "tooltip": "C'est ici que s'écrit le programme principal. Les blocs en dehors de celui-ci ne seront pas exécutés",
    "helpUrl": ""
  },
  {
    "type": "is_in_list",
    "message0": "l'élément %1 est dans %2",
    "args0": [
      {
        "type": "input_value",
        "name": "ITEM",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "LIST",
        "align": "CENTRE"
      }
    ],
    "inputsInline": true,
    "output": "Boolean",
    "colour": 230,
    "tooltip": "",
    "helpUrl": ""
  }
]);
