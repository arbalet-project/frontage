import { existsSync, writeJsonSync } from "std/fs/mod.ts";
import { blue } from "std/fmt/colors.ts";

if(!existsSync("config.json")) {
    console.log(blue("It seems you launch the application for the first time. \nBegin to initialize..."));
    writeJsonSync("config.json", { width: 19});
}

// console.log(existsSync("config.json"));