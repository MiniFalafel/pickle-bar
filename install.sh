#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Install dependencies
pacman -S - < "$SCRIPT_DIR/pkglist.txt"
# Install AUR dependencies as non-root user
NON_ROOT=$(who am i | awk '{print $1}')
sudo -u $NON_ROOT yay -S - < "$SCRIPT_DIR/yay-pkglist.txt"

