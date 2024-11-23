#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Install dependencies
if test -f "$SCRIPT_DIR/pkglist.txt"; then
    pacman -S - < "$SCRIPT_DIR/pkglist.txt"
fi
# Install AUR dependencies as non-root user
if test -f "$SCRIPT_DIR/yay-pkglist.txt"; then
    NON_ROOT=$(who am i | awk '{print $1}')
    sudo -u $NON_ROOT bash -c "yay -S - < $SCRIPT_DIR/yay-pkglist.txt"
fi

