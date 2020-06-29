#!/bin/bash

deno run --importmap=import_map.json --unstable --allow-read=config.json --allow-write=config.json mod.ts