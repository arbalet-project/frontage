import { existsSync, writeJsonSync } from "std/fs/mod.ts";
import { blue, yellow, red } from "std/fmt/colors.ts";
import Ask from "ask/mod.ts";

const version = "1.6.0";

if (!existsSync("config.json")) {
  const ask = new Ask();
  console.log(blue("It seems you launch the backend for the first time."));
  console.log(blue(`Initialization of Arbalet backend version : ${version}`));

  let { width, height } = await ask.prompt([
    {
      name: "width",
      type: "number",
      message: yellow("Enter width of your frontage (number of rows)"),
      min: 1,
    },
    {
      name: "height",
      type: "number",
      message: yellow("Enter height of your frontage (number of cols))"),
      min: 1,
    },
  ]);

  // TODO : width and height 

  while (true) {
    let { answer } = await ask.confirm({
      name: "answer",
      message: "Do you want to continue disabled pixels?",
      accept: "y",
      deny: "N",
      default: "N",
    });

    if (!answer) {
      break;
    } else {
      let { row, col } = await ask.prompt([
        {
          type: "number",
          name: "row",
          message: "Enter disabled pixel's row",
          min: 0,
          max: width,
        },
        {
          type: "number",
          name: "col",
          message: "Enter disabled pixel's col",
          min: 0,
          max: height,
        },
      ]);

      // TODO : row, col
    }
  }

  //writeJsonSync("config.json", { width, height });
}

// console.log(existsSync("config.json"));
