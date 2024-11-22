#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
config=$SCRIPT_DIR/bar.json
style=$SCRIPT_DIR/style.css

killall waybar
waybar -c "$config" -s "$style"
