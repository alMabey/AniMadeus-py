#!/bin/bash

# Kill running instance of the bot
kill -9 `cat pid.txt`
rm pid.txt

# Run bot and store pid
nohup ./venv/bin/python ./animadeus.py &
echo $! > pid.txt