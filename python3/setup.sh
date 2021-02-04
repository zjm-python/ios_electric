#!/bin/bash

echo "start install libimobiledevice"
brew install --HEAD libimobiledevice

echo "start install pyecharts........"
pip install wheel
pip install pyecharts==0.1.9.4
pip install pyecharts -U

echo "finish setup"
