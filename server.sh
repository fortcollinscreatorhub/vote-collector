#!/bin/bash

cd `dirname $0`
while true; do
  ./server.py
  echo Sleep before restart...
  sleep 1
done
