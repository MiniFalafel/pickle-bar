#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
config=$SCRIPT_DIR/bar.json
style=$SCRIPT_DIR/style.css

killall waybar
# Our waybar config needs this variable, so we're setting it before calling waybar
export WB_SCRIPT_PATH=$SCRIPT_DIR/scripts
waybar -c "$config" -s "$style"
