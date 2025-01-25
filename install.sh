#!/bin/bash

APP_NAME="car"
APP_PATH="./cscript.car"

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root or with sudo."
  exit 1
fi

if [ ! -f "$APP_PATH" ]; then
  echo "Error: $APP_PATH not found in the current directory."
  exit 1
fi

chmod +x "$APP_PATH"

prompt_yes_no() {
  while true; do
    read -p "$1 (y/n): " choice
    case "$choice" in
      [Yy]* ) return 0;;  # Yes
      [Nn]* ) return 1;;  # No
      * ) echo "Please answer y or n.";;
    esac
  done
}

if prompt_yes_no "Do You Want To Install CarbonScript?"; then
  cp "$APP_PATH" /usr/local/bin/"$APP_NAME"
else
  echo -e "\033[91mInstallation Aborted\033[0m"
fi

if [ -f "/usr/local/bin/$APP_NAME" ]; then
  echo -e "\033[92m CarbonScript has been successfully installed\033[0m"
  echo -e "\033[0m You can run it by typing: \033[93m$APP_NAME\033[0m"
  echo -e "\033[0m For more information type: \033[93m$APP_NAME --help\033[0m"
  exit 0
else
  echo "Error: Failed to move $APP_NAME to /usr/local/bin."
  exit 1
fi
