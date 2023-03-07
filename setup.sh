#!/bin/sh
PLUGIN_RELEASE="https://github.com/dewolf-research/rikai-joern/releases/latest/download/rikai-joern.zip"
ZIP_NAME="rikai-joern.zip"
PLUGIN_DIR="rikai-joern/"

curl -L $PLUGIN_RELEASE --output $ZIP_NAME
unzip -d $PLUGIN_DIR $ZIP_NAME

rm $ZIP_NAME